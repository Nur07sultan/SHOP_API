from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, CategoryWithCountSerializer, 
    ProductSerializer, ProductWithReviewsSerializer, 
    ReviewSerializer
)
from .validators import validate_positive_integer_id


def validate_request_content_type(request):
    """
    Валидация Content-Type для POST/PUT/PATCH запросов
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type = request.content_type
        if content_type and 'application/json' not in content_type:
            return False, {'error': 'Content-Type должен быть application/json'}
    return True, {}


def validate_request_data_not_empty(request):
    """
    Проверка, что данные запроса не пустые
    """
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.data:
            return False, {'error': 'Данные запроса не могут быть пустыми'}
    return True, {}


def validate_object_id(object_id, model_name='объект'):
    """
    Валидация ID объекта
    """
    try:
        validate_positive_integer_id(object_id)
        return True, {}
    except ValidationError as e:
        return False, {'error': f'Некорректный ID {model_name}: {str(e)}'}


# Category
class CategoryListView(APIView):
    # Возвращает список всех категорий с количеством товаров
    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategoryWithCountSerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении списка категорий',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Создание новой категории
    def post(self, request):
        # Валидация запроса
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                serializer = CategorySerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при создании категории',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryDetailView(APIView):
    # Детальная информация по одной категории
    def get(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'категории')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=id)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении категории',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Полное обновление категории
    def put(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'категории')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = CategorySerializer(category, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при обновлении категории',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Частичное обновление категории
    def patch(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'категории')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = CategorySerializer(category, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при частичном обновлении категории',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Удаление категории
    def delete(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'категории')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Проверяем, есть ли товары в этой категории
            if category.products.exists():
                return Response({
                    'error': 'Нельзя удалить категорию, в которой есть товары',
                    'products_count': category.products.count()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                category.delete()
                return Response({
                    'message': 'Категория успешно удалена'
                }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при удалении категории',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Product
class ProductListView(APIView):
    # Список всех товаров
    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении списка товаров',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Создание нового товара
    def post(self, request):
        # Валидация запроса
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                serializer = ProductSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при создании товара',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDetailView(APIView):
    # Детальная информация по товару
    def get(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'товара')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении товара',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Полное обновление товара
    def put(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'товара')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = ProductSerializer(product, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при обновлении товара',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Частичное обновление товара
    def patch(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'товара')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = ProductSerializer(product, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при частичном обновлении товара',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Удаление товара
    def delete(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'товара')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Проверяем, есть ли отзывы к этому товару
            if product.reviews.exists():
                return Response({
                    'error': 'Нельзя удалить товар, к которому есть отзывы',
                    'reviews_count': product.reviews.count()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                product.delete()
                return Response({
                    'message': 'Товар успешно удалён'
                }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при удалении товара',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Новый view для списка товаров с отзывами и рейтингом
class ProductWithReviewsListView(APIView):
    # Возвращает список всех товаров с их отзывами и средним рейтингом
    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductWithReviewsSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении товаров с отзывами',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Review
class ReviewListView(APIView):
    # Список всех отзывов
    def get(self, request):
        try:
            reviews = Review.objects.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении списка отзывов',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Создание нового отзыва
    def post(self, request):
        # Валидация запроса
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                serializer = ReviewSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при создании отзыва',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewDetailView(APIView):
    # Детальный отзыв по id
    def get(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'отзыва')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review = Review.objects.get(id=id)
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        except Review.DoesNotExist:
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при получении отзыва',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Полное обновление отзыва
    def put(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'отзыва')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = ReviewSerializer(review, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при обновлении отзыва',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Частичное обновление отзыва
    def patch(self, request, id):
        # Валидация запроса и ID
        is_valid, error_response = validate_object_id(id, 'отзыва')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_content_type(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid, error_response = validate_request_data_not_empty(request)
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                serializer = ReviewSerializer(review, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при частичном обновлении отзыва',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Удаление отзыва
    def delete(self, request, id):
        # Валидация ID
        is_valid, error_response = validate_object_id(id, 'отзыва')
        if not is_valid:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                review.delete()
                return Response({
                    'message': 'Отзыв успешно удалён'
                }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Произошла ошибка при удалении отзыва',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

