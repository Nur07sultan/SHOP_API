"""
Утилиты для обработки ошибок и валидации в Shop API
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для API
    """
    # Получаем стандартный ответ DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'timestamp': timezone.now().isoformat(),
            'path': context['request'].path,
            'method': context['request'].method,
        }
        
        # Обработка различных типов ошибок
        if response.status_code == 404:
            custom_response_data.update({
                'message': 'Ресурс не найден',
                'details': response.data
            })
        elif response.status_code == 400:
            custom_response_data.update({
                'message': 'Ошибка валидации данных',
                'details': response.data
            })
        elif response.status_code == 401:
            custom_response_data.update({
                'message': 'Необходима аутентификация',
                'details': response.data
            })
        elif response.status_code == 403:
            custom_response_data.update({
                'message': 'Доступ запрещён',
                'details': response.data
            })
        elif response.status_code == 405:
            custom_response_data.update({
                'message': 'Метод не разрешён',
                'details': response.data
            })
        elif response.status_code == 429:
            custom_response_data.update({
                'message': 'Превышен лимит запросов',
                'details': response.data
            })
        elif response.status_code >= 500:
            custom_response_data.update({
                'message': 'Внутренняя ошибка сервера',
                'details': 'Обратитесь к администратору'
            })
            # Логируем серверные ошибки
            logger.error(f'Server error: {exc}', exc_info=True)
        else:
            custom_response_data.update({
                'message': 'Произошла ошибка',
                'details': response.data
            })
        
        response.data = custom_response_data
    
    return response


def validate_json_request(request):
    """
    Валидация JSON запроса
    """
    if request.content_type != 'application/json':
        raise ValidationError('Content-Type должен быть application/json')
    
    if not request.body:
        raise ValidationError('Тело запроса не может быть пустым')
    
    try:
        import json
        json.loads(request.body)
    except json.JSONDecodeError:
        raise ValidationError('Некорректный JSON формат')


def log_api_request(request, response=None, error=None):
    """
    Логирование API запросов
    """
    log_data = {
        'method': request.method,
        'path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'ip': get_client_ip(request),
        'timestamp': timezone.now().isoformat()
    }
    
    if response:
        log_data['status_code'] = response.status_code
    
    if error:
        log_data['error'] = str(error)
        logger.error(f'API Error: {log_data}')
    else:
        logger.info(f'API Request: {log_data}')


def get_client_ip(request):
    """
    Получение IP адреса клиента
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_input(value):
    """
    Очистка входных данных от потенциально опасных символов
    """
    if isinstance(value, str):
        # Удаляем HTML теги
        import re
        value = re.sub(r'<[^>]+>', '', value)
        
        # Удаляем потенциально опасные SQL символы
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        # Обрезаем лишние пробелы
        value = value.strip()
    
    return value


class ValidationErrorMessages:
    """
    Константы с сообщениями об ошибках валидации
    """
    
    # Общие ошибки
    REQUIRED_FIELD = 'Это поле обязательно для заполнения'
    INVALID_FORMAT = 'Неверный формат данных'
    
    # Ошибки категорий
    CATEGORY_NAME_REQUIRED = 'Название категории обязательно'
    CATEGORY_NAME_TOO_SHORT = 'Название категории слишком короткое (минимум 2 символа)'
    CATEGORY_NAME_TOO_LONG = 'Название категории слишком длинное (максимум 100 символов)'
    CATEGORY_NAME_EXISTS = 'Категория с таким названием уже существует'
    
    # Ошибки товаров
    PRODUCT_TITLE_REQUIRED = 'Название товара обязательно'
    PRODUCT_TITLE_TOO_SHORT = 'Название товара слишком короткое (минимум 3 символа)'
    PRODUCT_TITLE_TOO_LONG = 'Название товара слишком длинное (максимум 100 символов)'
    PRODUCT_DESCRIPTION_REQUIRED = 'Описание товара обязательно'
    PRODUCT_DESCRIPTION_TOO_SHORT = 'Описание товара слишком короткое (минимум 10 символов)'
    PRODUCT_PRICE_REQUIRED = 'Цена товара обязательна'
    PRODUCT_PRICE_POSITIVE = 'Цена товара должна быть положительной'
    PRODUCT_CATEGORY_REQUIRED = 'Категория товара обязательна'
    
    # Ошибки отзывов
    REVIEW_TEXT_REQUIRED = 'Текст отзыва обязателен'
    REVIEW_TEXT_TOO_SHORT = 'Текст отзыва слишком короткий (минимум 5 символов)'
    REVIEW_STARS_REQUIRED = 'Рейтинг отзыва обязателен'
    REVIEW_STARS_RANGE = 'Рейтинг должен быть от 1 до 5 звёзд'
    REVIEW_PRODUCT_REQUIRED = 'Товар для отзыва обязателен'


def format_validation_errors(errors):
    """
    Форматирование ошибок валидации для удобного чтения
    """
    formatted_errors = {}
    
    for field, field_errors in errors.items():
        if isinstance(field_errors, list):
            formatted_errors[field] = field_errors
        else:
            formatted_errors[field] = [str(field_errors)]
    
    return formatted_errors