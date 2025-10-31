from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    ProductListView, ProductDetailView, ProductWithReviewsListView,
    ReviewListView, ReviewDetailView
)

# Маршруты приложения product (REST-подобные):
# - /categories/        GET -> список категорий с количеством товаров
# - /categories/<id>/   GET -> одна категория
# - /products/          GET -> список товаров
# - /products/<id>/     GET -> один товар
# - /products/reviews/  GET -> список товаров с отзывами и рейтингом
# - /reviews/           GET -> список отзывов
# - /reviews/<id>/      GET -> один отзыв
urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/<int:id>/', CategoryDetailView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/<int:id>/', ProductDetailView.as_view()),
    path('products/reviews/', ProductWithReviewsListView.as_view()),
    path('reviews/', ReviewListView.as_view()),
    path('reviews/<int:id>/', ReviewDetailView.as_view()),
]
