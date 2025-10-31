from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Category, Product, Review


# Сериализаторы преобразуют модели в JSON и обратно.
# Здесь используются ModelSerializer с полем fields='__all__',
# чтобы включить все поля модели в выходной JSON.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# Новый сериализатор для категорий с подсчётом товаров
class CategoryWithCountSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']
    
    def get_products_count(self, obj):
        # Подсчитываем количество товаров в данной категории
        return obj.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# Новый сериализатор для товаров с отзывами и средним рейтингом
class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'reviews', 'rating']
    
    def get_reviews(self, obj):
        # Получаем все отзывы для этого товара
        reviews = obj.reviews.all()
        return ReviewSerializer(reviews, many=True).data
    
    def get_rating(self, obj):
        # Вычисляем средний рейтинг всех отзывов
        avg_rating = obj.reviews.aggregate(Avg('stars'))['stars__avg']
        return round(avg_rating, 2) if avg_rating else 0.0


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
