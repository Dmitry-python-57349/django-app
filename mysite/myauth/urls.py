from django.urls import path


from .views import (
    AccountView,
    AboutMeView,
    RegisterView,
    login_view,
    logout_view,
    ProfileUpdateView,
    AllProfilesView,
    ProfileInfoView,
    ProfileInfoUpdateView,
)

app_name = "myauth"

urlpatterns = [
    path("", AccountView.as_view(), name="accounts"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("registration/", RegisterView.as_view(), name="registration"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("about-me/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("profiles/", AllProfilesView.as_view(), name="profiles"),
    path("profiles/<int:pk>/info/", ProfileInfoView.as_view(), name="profiles-info"),
    path("profiles/<int:pk>/info/update/", ProfileInfoUpdateView.as_view(), name="profiles-info-update"),
]
