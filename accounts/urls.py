from django.urls import path
from .views import LoginView, MeView, LogoutView, GoogleLoginView

urlpatterns = [
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
