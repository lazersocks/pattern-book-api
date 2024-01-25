from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from .models import *
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.mail import outbox
from .tasks import send_purchase_email
from unittest.mock import patch
from django.conf import settings

# Testing auth endpoints.


class UserAuthTests(APITestCase):
    def test_user_registration(self):
        url = reverse("auth_register")
        data = {
            "username": "testuser",
            "password": "testpassword123",
            "email": "test@email.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")

    def test_user_login_logout(self):
        self.test_user_registration()  # First, create a user
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)

        refresh_token = response.data.get("refresh")
        url = reverse("logout")
        data = {"refresh": str(refresh_token)}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)


# Testing Shopping Cart and Book crud
class BookstoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser1", password="testpassword1", email="test1@email.com"
        )
        self.client.force_authenticate(user=self.user)
        self.author = Author.objects.create(name="Test Author")
        self.category = Category.objects.create(name="Test Category")

    def test_view_cart_empty(self):
        response = self.client.get("/api/view_cart/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Shopping cart is empty.")

    def test_add_to_cart(self):
        book = Book.objects.create(
            title="Test Book",
            isbn="1234567890",
            author=self.author,
            category=self.category,
            published_date="2024-01-01",
        )
        response = self.client.post("/api/add_to_cart/", {"book_id": book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["book"]["title"], "Test Book")
        self.assertEqual(response.data["quantity"], 1)

    def test_remove_from_cart(self):
        book = Book.objects.create(
            title="Test Book",
            isbn="1234567890",
            author=self.author,
            category=self.category,
            published_date="2024-01-01",
        )
        shopping_cart = ShoppingCart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=shopping_cart, book=book)
        response = self.client.post("/api/remove_from_cart/", {"book_id": book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["book"]["title"], "Test Book")
        self.assertEqual(response.data["quantity"], 1)

    def test_checkout_empty_cart(self):
        response = self.client.get("/api/checkout/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Shopping cart is empty.")

    def test_checkout_successful(self):
        book = Book.objects.create(
            title="Test Book",
            isbn="1234567890",
            author=self.author,
            category=self.category,
            published_date="2024-01-01",
        )
        shopping_cart = ShoppingCart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=shopping_cart, book=book)
        response = self.client.get("/api/checkout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Checkout successful.")


# Testing Celery Task
class TestSendPurchaseEmailTask(TestCase):
    @patch("api.tasks.send_mail")
    def test_send_purchase_email(self, mock_send_mail):
        user_email = "test@example.com"
        cart_items = [
            ["Book Title 1", 2, "1234567890123"],
            ["Book Title 2", 1, "9876543210987"],
        ]

        send_purchase_email(user_email, cart_items)

        # Check that send_mail was called once
        self.assertTrue(mock_send_mail.called)

        # Check that send_mail was called with the correct arguments
        subject = "Your Purchase Details"
        message = "Thank you for your purchase. Here are the details:\n"
        message += "- Book Title 1 (Quantity: 2 - ISBN: 1234567890123) \n\n"
        message += "- Book Title 2 (Quantity: 1 - ISBN: 9876543210987) \n"

        mock_send_mail.assert_called_once_with(
            subject, message, settings.EMAIL_HOST_USER, [user_email]
        )


# Testing Author Crud
class AuthorViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.client.login(username="testuser", password="testpassword123")
        self.client.force_authenticate(user=self.user)
        Author.objects.create(name="Author 1")
        Author.objects.create(name="Author 2")

    def test_list_authors(self):
        self.client.force_authenticate(user=self.user)
        url = "/api/authors/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_author(self):
        self.client.force_authenticate(user=self.user)
        author = Author.objects.get(name="Author 1")
        url = f"/api/authors/{author.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Author 1")

    def test_create_author(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("author-list")
        data = {"name": "Author 3"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(Author.objects.get(id=3).name, "Author 3")

    def test_update_author(self):
        self.client.force_authenticate(user=self.user)
        author = Author.objects.get(name="Author 1")
        url = reverse("author-detail", args=[author.id])
        data = {"name": "Author 1 Updated"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(author.name, "Author 1 Updated")

    def test_delete_author(self):
        self.client.force_authenticate(user=self.user)
        author = Author.objects.get(name="Author 1")
        url = reverse("author-detail", args=[author.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 1)
