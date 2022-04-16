from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField, QuerySet
from django_lifecycle import hook, BEFORE_CREATE, BEFORE_UPDATE, LifecycleModelMixin
from enumfields import EnumField
from phonenumber_field.modelfields import PhoneNumberField

from foodcartapp.enums import OrderStatus, PaymentMethod
from restaurateur.fetch_coordinates import fetch_coordinates


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


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
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingredients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self) -> str:
        return self.name


class RestaurantMenuItem(models.Model):
    availability = models.BooleanField('в продаже', default=True, db_index=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product'],
        ]

    def __str__(self) -> str:
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):
    def total_cost(self) -> QuerySet:
        return self.annotate(
            total_cost=Sum(F('order_items__product_cost') * F('order_items__quantity'), output_field=DecimalField()),
        )


class Order(models.Model):
    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=100)
    phonenumber = PhoneNumberField(verbose_name='телефон')
    address = models.CharField('адрес', max_length=150)
    order_status = EnumField(OrderStatus, max_length=20, default=OrderStatus.incomplete, verbose_name='статус заказа')
    comment = models.TextField('комментарии', blank=True)
    payment_method = EnumField(PaymentMethod, max_length=20, default=PaymentMethod.card, verbose_name='метод оплаты')
    create_time = models.DateTimeField('заказ поступил', auto_now=True, blank=True)
    call_time = models.DateTimeField('связались с клиентом', blank=True, null=True)
    delivery_time = models.DateTimeField('заказ отправлен', blank=True, null=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

        indexes = [
            models.Index(fields=['order_status', 'create_time', 'call_time', 'delivery_time']),
        ]

    def __str__(self) -> str:
        return f'{self.lastname} {self.firstname}'


class OrderItem(models.Model):
    quantity = models.IntegerField('количество', validators=[MinValueValidator(1)])
    product_cost = models.DecimalField(
        'стоимость 1ед',
        max_digits=8,
        decimal_places=2,
        null=True,
        validators=[MinValueValidator(0)],
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='заказ')
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )

    def __str__(self) -> str:
        return self.product.name


class Banner(models.Model):
    src = models.ImageField('баннер', upload_to='banners/')
    title = models.CharField('название', max_length=200)
    description = models.TextField('описание')
    banner_order = models.PositiveIntegerField(default=0, verbose_name='место баннера', db_index=True)

    class Meta:
        ordering = ['banner_order']
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'

    def __str__(self) -> str:
        return f'{self.title}'


class Location(LifecycleModelMixin, models.Model):
    restaurant_address = models.CharField('адрес ресторана', max_length=200)
    restaurant_lon = models.FloatField('долгота ресторана', blank=True, null=True)
    restaurant_lat = models.FloatField('широта ресторана', blank=True, null=True)
    delivery_address = models.CharField('адрес доставки', max_length=200)
    delivery_lon = models.FloatField('долгота доставки', blank=True, null=True)
    delivery_lat = models.FloatField('широта доставки', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant_address', 'delivery_address']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant_address', 'delivery_address'],
                name='unique_couple_addresses',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.restaurant_address=}, {self.delivery_address=}'

    @hook(BEFORE_CREATE)
    @hook(BEFORE_UPDATE)
    def create_geo_address(self) -> None:
        self.restaurant_lon, self.restaurant_lat = fetch_coordinates(self.restaurant_address)
        self.delivery_lon, self.delivery_lat = fetch_coordinates(self.delivery_address)
