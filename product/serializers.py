from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Category, Product, Review
from .validators import (
    validate_category_name, validate_product_title, validate_product_description,
    validate_product_price, validate_review_text, validate_review_stars,
    NoHTMLValidator, NoSQLInjectionValidator, validate_request_data_size
)


# Сериализаторы преобразуют модели в JSON и обратно.
# С улучшенной валидацией для всех полей
class CategorySerializer(serializers.ModelSerializer):
    # Применяем кастомную валидацию к полю name
    name = serializers.CharField(
        max_length=100,
        validators=[
            validate_category_name,
            NoHTMLValidator('HTML теги не разрешены в названии категории'),
            NoSQLInjectionValidator('Недопустимые символы в названии категории')
        ]
    )
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def validate(self, data):
        """
        Валидация на уровне сериализатора
        """
        # Проверяем размер данных
        validate_request_data_size(data)
        
        return data
    
    def validate_name(self, value):
        """
        Валидация уникальности названия категории
        """
        name = value.strip().lower()
        if name:
            # При обновлении исключаем текущий объект из проверки
            queryset = Category.objects.filter(name__iexact=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    'Категория с таким названием уже существует'
                )
        
        return value


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
    # Применяем кастомную валидацию ко всем полям товара
    title = serializers.CharField(
        max_length=100,
        validators=[
            validate_product_title,
            NoHTMLValidator('HTML теги не разрешены в названии товара'),
            NoSQLInjectionValidator('Недопустимые символы в названии товара')
        ]
    )
    
    description = serializers.CharField(
        validators=[
            validate_product_description,
            NoHTMLValidator('HTML теги не разрешены в описании товара'),
            NoSQLInjectionValidator('Недопустимые символы в описании товара')
        ]
    )
    
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_product_price]
    )
    
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={
            'does_not_exist': 'Указанная категория не существует',
            'incorrect_type': 'ID категории должен быть числом',
            'required': 'Категория обязательна для заполнения'
        }
    )
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate(self, data):
        """
        Валидация на уровне сериализатора для товаров
        """
        # Проверяем размер данных
        validate_request_data_size(data)
        
        return data
    
    def validate_title(self, value):
        """
        Валидация уникальности названия товара в рамках категории
        """
        return value  # Уникальность проверяется в validate() после получения category


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
    # Применяем кастомную валидацию ко всем полям отзыва
    text = serializers.CharField(
        validators=[
            validate_review_text,
            NoHTMLValidator('HTML теги не разрешены в тексте отзыва'),
            NoSQLInjectionValidator('Недопустимые символы в тексте отзыва')
        ]
    )
    
    stars = serializers.IntegerField(
        validators=[validate_review_stars]
    )
    
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={
            'does_not_exist': 'Указанный товар не существует',
            'incorrect_type': 'ID товара должен быть числом',
            'required': 'Товар обязателен для заполнения'
        }
    )
    
    class Meta:
        model = Review
        fields = '__all__'
    
    def validate(self, data):
        """
        Валидация на уровне сериализатора для отзывов
        """
        # Проверяем размер данных
        validate_request_data_size(data)
        
        # Дополнительная бизнес-логика: один пользователь - один отзыв на товар
        # (пока без аутентификации, но структура готова)
        product = data.get('product')
        text = data.get('text', '').strip().lower()
        
        if product and text:
            # Проверяем на дублированные отзывы с похожим текстом
            similar_reviews = Review.objects.filter(
                product=product,
                text__iexact=text
            )
            # При обновлении исключаем текущий объект
            if self.instance:
                similar_reviews = similar_reviews.exclude(pk=self.instance.pk)
            
            if similar_reviews.exists():
                raise serializers.ValidationError({
                    'text': 'Отзыв с похожим текстом уже существует для данного товара'
                })
        
        return data
