from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingredients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items') 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('UP', 'Необработанный'),
        ('PR', 'Обработанный'),
    ]
    PAYMENT_METHOD = [
        ('CA', 'Наличные'),
        ('CC', 'Электронно')
    ]

    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=100)
    phonenumber = PhoneNumberField(verbose_name='телефон')
    address = models.CharField('адрес', max_length=150)
    order_status = models.CharField('статус', max_length=3, choices=ORDER_STATUS_CHOICES, default='Необработанный', db_index=True)
    comment = models.TextField('комментарии', blank=True)
    payment_method = models.CharField('тип оплаты', max_length=2, choices=PAYMENT_METHOD, default='Электронно')

    create_time = models.DateTimeField('заказ поступил', auto_now=True, blank=True)
    call_time = models.DateTimeField('связались с клиентом', blank=True, null=True)
    delivery_time = models.DateTimeField('заказ отправлен', blank=True, null=True)

    def __str__(self):
        return f'{self.lastname} {self.firstname}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    quantity = models.IntegerField('количество', validators=[MinValueValidator(1), MaxValueValidator(10)])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='заказ')
    product_cost = models.DecimalField(
        'стоимость 1ед',
        max_digits=8,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.product.name


class Banner(models.Model):
    src = models.ImageField('баннер', upload_to='banners/')
    title = models.CharField('название', max_length=200)
    description = models.TextField('описание')
    banner_order = models.PositiveIntegerField(default=0, verbose_name='место баннера', db_index=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['banner_order']
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'


class Location(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['restaurant_address', 'delivery_address'])
        ]
    restaurant_address = models.CharField('адрес ресторана', max_length=200)
    restaurant_lon = models.FloatField('долгота ресторана')
    restaurant_lat = models.FloatField('широта ресторана')
    delivery_address = models.CharField('адрес доставки', max_length=200)
    delivery_lon = models.FloatField('долгота доставки')
    delivery_lat = models.FloatField('широта доставки')