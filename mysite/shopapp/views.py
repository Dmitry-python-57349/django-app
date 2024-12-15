from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Order
from .serializers import OrderSerializer


class ShopIndexView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {}
        return render(request, "shopapp/shop-index.html", context=context)


class ProductDetailsView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_product"]
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"


class ProductsListView(PermissionRequiredMixin, ListView):
    permission_required = ["shopapp.view_product"]
    ordering = ["pk",]
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ["shopapp.add_product", ]
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request._cached_user
        response = super().form_valid(form)
        return response


class ProductUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ["shopapp.change_product", ]
    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ["shopapp.delete_product", ]
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/user_orders_list.html"
    context_object_name = "orders"

    def get_success_url(self):
        return reverse(
            "shopapp:user_orders",
            kwargs={"user_id": self.request.user.id},
        )

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs.get("user_id"))
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context.update(
            {
                "owner": self.owner,
            }
        )
        return context


class UserOrdersListExport(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, **kwargs) -> JsonResponse:
        self.owner = get_object_or_404(User, pk=kwargs.get("user_id"))
        cache_key = f"user_orders_export_{self.owner}"
        orders_data = cache.get(cache_key)
        if orders_data is None:
            user_orders = Order.objects.filter(user=self.owner).order_by("pk")
            orders_data = OrderSerializer(user_orders, many=True).data
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({"orders": orders_data})


class OrdersListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    permission_required = ["shopapp.view_order", ]
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    permission_required = ["shopapp.view_order", ]
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
