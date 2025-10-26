from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    ProductListView, ProductDetailView,
    ReviewListView, ReviewDetailView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/<int:id>/', CategoryDetailView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/<int:id>/', ProductDetailView.as_view()),
    path('reviews/', ReviewListView.as_view()),
    path('reviews/<int:id>/', ReviewDetailView.as_view()),
]
