from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)

products_list = views.ProductViewSet.as_view({"get": "list", "post": "create"})
products_detail = views.ProductViewSet.as_view(
    {"patch": "partial_update", "delete": "destroy", "get": "retrieve"}
)

urlpatterns = [
    path("", include(router.urls)),
    path("products/", products_list, name="products-list"),
    path("products/<int:pk>/", products_detail, name="products-detail"),
]
