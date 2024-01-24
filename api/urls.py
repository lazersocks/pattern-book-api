from django.urls import path, include
from .views import *
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.conf import settings
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"books", BookViewSet)
router.register(r"authors", AuthorViewSet)
router.register(r"categories", CategoryViewSet)

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", BlacklistTokenUpdateView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("welcome/", welcome, name="welcome"),
    path("", include(router.urls)),
    path("view_cart/", view_cart, name="view_cart"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("remove_from_cart/", remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout, name="checkout"),
]
