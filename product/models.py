from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('название'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('заголовок'))
    description = models.TextField(verbose_name=_('описание'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('цена'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('категория'))

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    def __str__(self):
        return self.title


class Review(models.Model):
    text = models.TextField(verbose_name=_('текст'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('товар'))
    # Рейтинг отзыва от 1 до 5 звёзд
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('рейтинг'),
        help_text='Рейтинг от 1 до 5 звёзд',
        default=5
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')

    def __str__(self):
        return f"{self.text[:50]} ({self.stars}★)"