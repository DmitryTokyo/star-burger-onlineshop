from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, DecimalField, QuerySet
from enumfields import EnumField
from phonenumber_field.modelfields import PhoneNumberField

from foodcartapp.enums import OrderStatus, PaymentMethod
from restaurateur.fetch_coordinates import fetch_coordinates


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)
    longitude = models.FloatField('долгота', blank=True, null=True)
    latitude = models.FloatField('широта', blank=True, null=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self) -> str:
        return self.name

    @property
    def coordinates(self) -> tuple[float | None, float | None]:
        if not self.longitude and not self.latitude:
            self.longitude, self.latitude = fetch_coordinates(self.address)
            self.save()

        return self.longitude, self.latitude


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self) -> str:
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


class DeliveryLocation(models.Model):
    address = models.CharField('адрес', max_length=200)
    longitude = models.FloatField('долгота', blank=True, null=True)
    latitude = models.FloatField('широта', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['address']),
        ]

    def __str__(self) -> str:
        return self.address

    @property
    def coordinates(self) -> tuple[float | None, float | None]:
        if not self.longitude and not self.latitude:
            self.longitude, self.latitude = fetch_coordinates(self.address)
            self.save()

        return self.longitude, self.latitude


class OrderQuerySet(models.QuerySet):
    def total_cost(self) -> QuerySet:
        return self.annotate(
            total_cost=Sum(F('items__product_cost') * F('items__quantity'), output_field=DecimalField()),
        )


class Order(models.Model):
    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=100)
    phonenumber = PhoneNumberField(verbose_name='телефон')
    address = models.CharField('адрес', max_length=150)
    order_status = EnumField(OrderStatus, max_length=20, default=OrderStatus.incomplete, verbose_name='статус заказа')
    comment = models.TextField('комментарии', blank=True)
    payment_method = EnumField(PaymentMethod, max_length=20, verbose_name='метод оплаты')
    create_time = models.DateTimeField('заказ поступил', auto_now=True, blank=True)
    call_time = models.DateTimeField('связались с клиентом', blank=True, null=True)
    delivery_time = models.DateTimeField('заказ отправлен', blank=True, null=True)
    delivery_location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

        indexes = [
            models.Index(fields=['order_status', 'create_time', 'call_time', 'delivery_time', 'phonenumber']),
        ]

    def __str__(self) -> str:
        return f'{self.lastname} {self.firstname}'


class OrderItem(models.Model):
    quantity = models.IntegerField('количество', validators=[MinValueValidator(1)])
    product_cost = models.DecimalField(
        'стоимость 1ед',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='заказ')
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
        return self.title
