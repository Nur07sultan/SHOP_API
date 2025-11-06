"""
Middleware для дополнительной валидации API запросов
"""

import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


logger = logging.getLogger(__name__)


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Middleware для валидации входящих запросов
    """
    
    def process_request(self, request):
        """
        Обработка входящего запроса
        """
        # Проверяем размер запроса
        max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 2621440)  # 2.5MB по умолчанию
        if hasattr(request, 'body') and len(request.body) > max_size:
            return JsonResponse({
                'error': f'Размер запроса превышает максимально допустимый ({max_size} байт)'
            }, status=413)
        
        # Проверяем Content-Type для POST/PUT/PATCH запросов к API
        if request.method in ['POST', 'PUT', 'PATCH'] and request.path.startswith('/api/'):
            content_type = request.content_type or ''
            if 'application/json' not in content_type and 'multipart/form-data' not in content_type:
                return JsonResponse({
                    'error': 'Неподдерживаемый Content-Type. Используйте application/json'
                }, status=400)
        
        return None
    
    def process_exception(self, request, exception):
        """
        Обработка исключений
        """
        if request.path.startswith('/api/'):
            logger.error(f'API Error: {exception}', exc_info=True)
            
            # Возвращаем общую ошибку для API без раскрытия деталей
            return JsonResponse({
                'error': 'Произошла внутренняя ошибка сервера',
                'timestamp': str(timezone.now()),
                'path': request.path
            }, status=500)
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления заголовков безопасности
    """
    
    def process_response(self, request, response):
        """
        Добавляем заголовки безопасности к ответу
        """
        if request.path.startswith('/api/'):
            # Предотвращение MIME-снiffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # Защита от XSS
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Предотвращение показа в iframe
            response['X-Frame-Options'] = 'DENY'
            
            # Строгая транспортная безопасность (только для HTTPS)
            if request.is_secure():
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # CSP для API (только JSON)
            response['Content-Security-Policy'] = "default-src 'none'"
            
            # Удаляем заголовки, которые могут раскрыть информацию о сервере
            response['Server'] = 'Shop API'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Простое ограничение частоты запросов
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}  # В продакшене лучше использовать Redis
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Проверка лимита запросов
        """
        if not request.path.startswith('/api/'):
            return None
        
        # Получаем IP адрес клиента
        ip = self.get_client_ip(request)
        current_time = int(time.time())
        window_size = 60  # 1 минута
        max_requests = 100  # максимум 100 запросов в минуту
        
        # Очищаем старые записи
        self.cleanup_old_requests(current_time - window_size)
        
        # Подсчитываем запросы для данного IP
        if ip not in self.request_counts:
            self.request_counts[ip] = []
        
        # Фильтруем запросы в текущем окне
        recent_requests = [
            timestamp for timestamp in self.request_counts[ip]
            if timestamp > current_time - window_size
        ]
        
        if len(recent_requests) >= max_requests:
            return JsonResponse({
                'error': 'Превышен лимит запросов. Попробуйте позже.',
                'retry_after': window_size
            }, status=429)
        
        # Добавляем текущий запрос
        self.request_counts[ip] = recent_requests + [current_time]
        
        return None
    
    def get_client_ip(self, request):
        """
        Получение IP адреса клиента
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def cleanup_old_requests(self, cutoff_time):
        """
        Очистка старых записей запросов
        """
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [
                timestamp for timestamp in self.request_counts[ip]
                if timestamp > cutoff_time
            ]
            if not self.request_counts[ip]:
                del self.request_counts[ip]


import time
from django.utils import timezone