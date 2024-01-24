from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from django.contrib.auth.models import User

from rest_framework import generics
from django.utils.decorators import method_decorator
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from .tasks import send_purchase_email


# Authentication
# login
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


# register
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# logout
class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"message": "Error logging out."}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def welcome(request):
    username = request.user.username
    return Response({"message": f"Welcome to the Bookstore, {username}!"})


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)

    if created:
        return Response(
            {"message": "Shopping cart is empty."}, status=status.HTTP_201_CREATED
        )
    else:
        cart_items = CartItem.objects.filter(cart=cart)
        return Response(
            CartItemSerializer(cart_items, many=True).data, status=status.HTTP_200_OK
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    try:
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        book_id = request.data["book_id"]
        book = Book.objects.get(id=book_id)
        cart_item = CartItem.objects.filter(cart=cart, book=book).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(cart=cart, book=book)
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response(
            {
                "message": "Error adding book to cart.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    try:
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        book_id = request.data["book_id"]
        book = Book.objects.get(id=book_id)
        cart_item = CartItem.objects.filter(cart=cart, book=book).first()
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response(
            {
                "message": "Error removing book from cart.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkout(request):
    try:
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if created or len(cart_items) == 0:
            return Response(
                {"message": "Shopping cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_items_list = CartItemSerializer(cart_items, many=True).data
        send_purchase_email.delay(request.user.email, list(cart_items_list))

        cart_items.delete()
        return Response({"message": "Checkout successful."}, status=status.HTTP_200_OK)
    except Exception as e:
        print("this is ", e)
        return Response(
            {
                "message": "Error removing book from cart.",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
