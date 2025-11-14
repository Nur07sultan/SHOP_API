from django.urls import path
from .views import RegisterView, LoginView, ConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('confirm/', ConfirmView.as_view(), name='user-confirm'),
]