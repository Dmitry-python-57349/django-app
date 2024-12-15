from django.urls import path

from .views import (
    ShopIndexView,
    ProductDetailsView,
    ProductsListView,
    OrdersListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    UserOrdersListView,
    UserOrdersListExport,
)

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/user/<int:user_id>/", UserOrdersListView.as_view(), name="user_orders"),
    path("orders/user/<int:user_id>/export/", UserOrdersListExport.as_view(), name="user_orders_export"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
]
