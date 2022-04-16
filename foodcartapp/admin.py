from adminsortable2.admin import SortableAdminMixin
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import SafeString

from foodcartapp.models import Restaurant, Product, RestaurantMenuItem, ProductCategory, Order, OrderItem, Banner


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
        RestaurantMenuItemInline,
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
        'name',
        'category',
    ]

    inlines = [
        RestaurantMenuItemInline,
    ]
    fieldsets = (
        (
            'Общее', {
                'fields': [
                    'name',
                    'category',
                    'image',
                    'get_image_preview',
                    'price',
                ],
            },
        ),
        (
            'Подробно', {
                'fields': [
                    'special_status',
                    'ingredients',
                ],
                'classes': [
                    'wide',
                ],
            },
        ),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            'all': (
                'admin/foodcartapp.css',
            ),
        }

    def get_image_preview(self, obj: Product) -> SafeString | str:
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" height="200"/>', url=obj.image.url)

    def get_image_list_preview(self, obj: Product) -> SafeString | str:  # noqa CCE001
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" height="50"/></a>', edit_url=edit_url, src=obj.image.url,
        )

    get_image_preview.short_description = 'превью'
    get_image_list_preview.short_description = 'превью'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
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

    inlines = [
        OrderItemInline,
    ]

    def response_change(self, request: HttpRequest, obj: Order) -> HttpResponseRedirect:
        response = super().response_change(request, obj)
        allowed_hosts = settings.ALLOWED_HOSTS
        try:
            has_url_allowed_host_and_scheme = url_has_allowed_host_and_scheme(
                request.GET['next'],
                allowed_hosts=allowed_hosts,
            )
        except AttributeError:
            return response
        else:
            if not has_url_allowed_host_and_scheme:
                return response
            return HttpResponseRedirect(request.GET['next'])


@admin.register(Banner)
class BannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    model = Banner
    readonly_fields = ['preview_image']
    list_display = ['preview_image', 'title']

    def preview_image(self, obj: Banner) -> SafeString:
        return format_html('<img src="{url}" width="250"/>', url=obj.src.url)


admin.site.register(ProductCategory)
