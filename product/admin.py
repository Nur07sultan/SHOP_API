from django.contrib import admin
from .models import Category, Product, Review

# Регистрируем модели в админке, чтобы можно было добавлять/редактировать записи


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	# показывать id и название в списке
	list_display = ('id', 'name')
	# поле для поиска
	search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	# показывать id, заголовок, цену и категорию
	list_display = ('id', 'title', 'price', 'category')
	# фильтр по категории
	list_filter = ('category',)
	# поиск по заголовку и описанию
	search_fields = ('title', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # показывать id, текст, рейтинг и связанный товар
    list_display = ('id', 'text', 'stars', 'product')
    # фильтр по рейтингу
    list_filter = ('stars',)
    search_fields = ('text',)
# Настройки интерфейса админки на русском
admin.site.site_header = 'Администрация магазина'
admin.site.site_title = 'Админка магазина'
admin.site.index_title = 'Управление моделями магазина'

