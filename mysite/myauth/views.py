from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView, UpdateView, View, ListView
from django.urls import reverse, reverse_lazy
from .models import Profile


class AccountView(TemplateView):
    template_name = "myauth/accounts.html"


class AboutMeView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        profile_pk = request.__dict__["user"].profile.pk
        context = {
            "profile": Profile.objects.get(pk=profile_pk),
        }
        return render(request, "myauth/about-me.html", context=context)


class ProfileInfoView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        context = {
            "profile": Profile.objects.get(pk=pk),
        }
        return render(request, "myauth/profiles-info.html", context=context)


class ProfileInfoUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ["myauth.change_profile",]
    model = Profile
    fields = "bio", "agreement_accepted", "avatar"
    template_name_suffix = "_info_update_form"

    def get_success_url(self):
        return reverse(
            "myauth:profiles-info",
            kwargs={"pk": self.object.pk},
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not kwargs:
            return HttpResponse("Permission denied!")
        pk = kwargs["pk"]
        profile_user = Profile.objects.get(pk=pk)
        if (self.request._cached_user is profile_user.user) or self.request._cached_user.is_staff:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
        context = {
            "profile": Profile.objects.get(pk=pk)
        }
        return render(request, "myauth/profiles-info.html", context=context)


class AllProfilesView(LoginRequiredMixin, ListView):
    template_name = "myauth/profiles-list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.all().select_related("user")


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/registration.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = User.objects.get(pk=self.object.pk)
        group = Group.objects.get(name="default_user")
        user.groups.add(group)

        group.save()
        user.save()

        user = authenticate(
            self.request,
            username=username,
            password=password,
        )

        login(request=self.request, user=user)
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = "bio", "agreement_accepted", "avatar"
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        form.instance.created_by = self.request._cached_user
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse(
            "myauth:profile-update",
            kwargs={"pk": self.object.pk},
        )


def login_view(request: HttpRequest) -> HttpResponse:
    context = {
        "form": ("username", "password"),
    }
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse("myauth:about-me"))

        return render(request, "myauth/login.html", context=context)

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(reverse("myauth:about-me"))

    context["error"] = "Invalid login credentials"
    return render(request, "myauth/login.html", context=context)


def logout_view(request: HttpRequest):
    print(request.user.user_permissions.__dict__)
    logout(request)
    return redirect(reverse("myauth:login"))
