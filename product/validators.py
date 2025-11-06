"""
Кастомные валидаторы для API эндпоинтов Shop API
"""

from rest_framework import serializers
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re


def validate_category_name(value):
    """
    Валидатор для названия категории
    """
    if not value or not value.strip():
        raise serializers.ValidationError('Название категории не может быть пустым')
    
    if len(value.strip()) < 2:
        raise serializers.ValidationError('Название категории должно содержать минимум 2 символа')
    
    if len(value.strip()) > 100:
        raise serializers.ValidationError('Название категории не может быть длиннее 100 символов')
    
    # Проверка на недопустимые символы
    if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-_]+$', value):
        raise serializers.ValidationError('Название категории содержит недопустимые символы')
    
    return value.strip()


def validate_product_title(value):
    """
    Валидатор для названия товара
    """
    if not value or not value.strip():
        raise serializers.ValidationError('Название товара не может быть пустым')
    
    if len(value.strip()) < 3:
        raise serializers.ValidationError('Название товара должно содержать минимум 3 символа')
    
    if len(value.strip()) > 100:
        raise serializers.ValidationError('Название товара не может быть длиннее 100 символов')
    
    # Проверка на недопустимые символы
    if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-_.,!?()]+$', value):
        raise serializers.ValidationError('Название товара содержит недопустимые символы')
    
    return value.strip()


def validate_product_description(value):
    """
    Валидатор для описания товара
    """
    if not value or not value.strip():
        raise serializers.ValidationError('Описание товара не может быть пустым')
    
    if len(value.strip()) < 10:
        raise serializers.ValidationError('Описание товара должно содержать минимум 10 символов')
    
    if len(value.strip()) > 1000:
        raise serializers.ValidationError('Описание товара не может быть длиннее 1000 символов')
    
    return value.strip()


def validate_product_price(value):
    """
    Валидатор для цены товара
    """
    if value is None:
        raise serializers.ValidationError('Цена товара обязательна')
    
    if value <= 0:
        raise serializers.ValidationError('Цена товара должна быть больше 0')
    
    if value > 999999.99:
        raise serializers.ValidationError('Цена товара не может превышать 999 999.99')
    
    # Проверка на максимум 2 знака после запятой
    if value * 100 != int(value * 100):
        raise serializers.ValidationError('Цена может содержать максимум 2 знака после запятой')
    
    return value


def validate_review_text(value):
    """
    Валидатор для текста отзыва
    """
    if not value or not value.strip():
        raise serializers.ValidationError('Текст отзыва не может быть пустым')
    
    if len(value.strip()) < 5:
        raise serializers.ValidationError('Текст отзыва должен содержать минимум 5 символов')
    
    if len(value.strip()) > 1000:
        raise serializers.ValidationError('Текст отзыва не может быть длиннее 1000 символов')
    
    # Проверка на спам (повторяющиеся символы)
    if re.search(r'(.)\1{4,}', value):
        raise serializers.ValidationError('Текст отзыва содержит подозрительные повторения символов')
    
    return value.strip()


def validate_review_stars(value):
    """
    Валидатор для рейтинга отзыва
    """
    if value is None:
        raise serializers.ValidationError('Рейтинг отзыва обязателен')
    
    if not isinstance(value, int):
        raise serializers.ValidationError('Рейтинг должен быть целым числом')
    
    if value < 1 or value > 5:
        raise serializers.ValidationError('Рейтинг должен быть от 1 до 5 звёзд')
    
    return value


def validate_positive_integer_id(value):
    """
    Валидатор для ID объектов
    """
    if value is None:
        raise serializers.ValidationError('ID обязателен')
    
    if not isinstance(value, int) and not str(value).isdigit():
        raise serializers.ValidationError('ID должен быть положительным числом')
    
    if int(value) <= 0:
        raise serializers.ValidationError('ID должен быть положительным числом')
    
    return int(value)


class NoHTMLValidator:
    """
    Валидатор для предотвращения HTML инъекций
    """
    def __init__(self, message=None):
        self.message = message or 'HTML теги не разрешены'
    
    def __call__(self, value):
        if re.search(r'<[^>]+>', str(value)):
            raise serializers.ValidationError(self.message)
        return value


class NoSQLInjectionValidator:
    """
    Валидатор для предотвращения SQL инъекций
    """
    def __init__(self, message=None):
        self.message = message or 'Обнаружены потенциально опасные символы'
    
    def __call__(self, value):
        dangerous_patterns = [
            r"'.*'",  # SQL quotes
            r'".*"',  # SQL double quotes
            r'--;',   # SQL comments
            r'\/\*.*\*\/',  # SQL block comments
            r'\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b',  # SQL keywords
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                raise serializers.ValidationError(self.message)
        return value


def validate_request_data_size(data, max_size_mb=1):
    """
    Валидатор для размера данных запроса
    """
    import json
    try:
        data_str = json.dumps(data)
        size_mb = len(data_str.encode('utf-8')) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise serializers.ValidationError(
                f'Размер данных запроса превышает {max_size_mb}MB'
            )
    except (TypeError, ValueError):
        # Если не удается сериализовать, пропускаем проверку
        pass
    return data