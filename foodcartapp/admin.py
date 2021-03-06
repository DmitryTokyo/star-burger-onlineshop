from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from adminsortable2.admin import SortableAdminMixin
from environs import Env

from .models import Restaurant, Product, RestaurantMenuItem, ProductCategory
from foodcartapp.models import Order, OrderProduct, Banner

env = Env()


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'ingredients',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                "admin/foodcartapp.css",
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" height="200"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" height="50"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    fields = ['product', 'quantity', 'product_cost']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = [
        'order_status',
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'comment',
        'payment_method',
        'create_time',
        'call_time',
        'delivery_time',
        ]
    readonly_fields = ['create_time']

    def response_change(self, request, obj):
        response = super(OrderAdmin, self).response_change(request, obj)
        allowed_hosts = settings.ALLOWED_HOSTS
        
        try:
            if not url_has_allowed_host_and_scheme(request.GET['next'], allowed_hosts=allowed_hosts):
                return response
            return HttpResponseRedirect(request.GET['next'])
        except Exception:
            return response
        
    inlines = [
        OrderProductInline
    ]

@admin.register(Banner)
class BannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    model = Banner
    readonly_fields = ['preview_image']
    list_display = ['preview_image', 'title']

    def preview_image(self, obj):
        return format_html('<img src="{url}" width="250"/>', url=obj.src.url)
