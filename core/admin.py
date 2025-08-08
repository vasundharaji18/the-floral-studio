from django.contrib import admin
from .models import *
from .models import SecondaryHero
from .models import NewsletterEmail
from .models import Footer
from .models import CartItem
#product
from .models import CarpetProduct
from .models import Carpet
from .models import GreenWall
from .models import SportsProduct
from .models import ArtificialPlant 


from .models import BusinessProfile

from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.urls import path

from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

from .models import SellingDetail, BuyingDetail, PaymentDetail, OrderDetail

admin.site.register(NavLink)

admin.site.register(HeroSlide)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Event)
admin.site.register(CartItem)

admin.site.register(SubscribeSection)
admin.site.register(Newsletter)
admin.site.register(FooterLink)
admin.site.register(SocialLink)
admin.site.register(SecondaryHero)
admin.site.register(NewsletterEmail)
admin.site.register(Footer)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)

#product
admin.site.register(CarpetProduct)
admin.site.register(Carpet)


admin.site.register(GreenWall)

admin.site.register(SportsProduct)


admin.site.register(ArtificialPlant) 


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Business Details', {
            'fields': ('business_name', 'phone_number', 'tin', 'email', 'logo')
        }),
        ('More Details', {
            'fields': ('business_type', 'business_address', 'signature')
        }),
    )

list_display = ('business_name', 'phone_number', 'email', 'business_type')


@admin.register(SellingDetail)
class SellingDetailAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'seller', 'quantity', 'price', 'sold_on')
    list_filter = ('sold_on', 'seller')
    search_fields = ('product_name',)

@admin.register(BuyingDetail)
class BuyingDetailAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'buyer', 'quantity', 'bought_on')
    list_filter = ('bought_on', 'buyer')
    search_fields = ('product_name',)

@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'payment_date')
    search_fields = ('order_id',)

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'status', 'order_date', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number',)



class CustomAdminSite(admin.AdminSite):
    site_header = "Floral Studio Admin"
    site_title = "Floral Studio Admin Portal"
    index_title = "Dashboard Overview"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_index), name='index'),
        ]
        # put our custom index at the top to override default index
        return custom_urls + urls

    def custom_index(self, request, extra_context=None):
        # Calculate summary stats
        total_selling = SellingDetail.objects.count()
        total_buying = BuyingDetail.objects.count()
        total_payments = PaymentDetail.objects.count()
        total_orders = OrderDetail.objects.count()

        # You can add latest records too if needed:
        latest_selling = SellingDetail.objects.order_by('-sold_on')[:5]
        latest_buying = BuyingDetail.objects.order_by('-bought_on')[:5]
        latest_payments = PaymentDetail.objects.order_by('-payment_date')[:5]
        latest_orders = OrderDetail.objects.order_by('-order_date')[:5]

        context = {
            **(extra_context or {}),
            'total_selling': total_selling,
            'total_buying': total_buying,
            'total_payments': total_payments,
            'total_orders': total_orders,
            'latest_selling': latest_selling,
            'latest_buying': latest_buying,
            'latest_payments': latest_payments,
            'latest_orders': latest_orders,
        }

        return TemplateResponse(request, "admin/custom_index.html", context)

# Instantiate and register your custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models with this custom admin site
from .models import BusinessProfile, SellingDetail, BuyingDetail, PaymentDetail, OrderDetail

custom_admin_site.register(BusinessProfile)
custom_admin_site.register(SellingDetail)
custom_admin_site.register(BuyingDetail)
custom_admin_site.register(PaymentDetail)
custom_admin_site.register(OrderDetail)


def custom_index(self, request, extra_context=None):
    # existing summary counts
    total_selling = SellingDetail.objects.count()
    total_buying = BuyingDetail.objects.count()
    total_payments = PaymentDetail.objects.count()
    total_orders = OrderDetail.objects.count()

    # last 6 months for x-axis labels
    today = now().date()
    months = []
    for i in range(5, -1, -1):
        month = (today.replace(day=1) - timedelta(days=i*30))
        months.append(month.strftime("%b %Y"))

    # Group selling count by month
    selling_data_qs = (
        SellingDetail.objects
        .annotate(month=TruncMonth('sold_on'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    selling_data = {item['month'].strftime("%b %Y"): item['count'] for item in selling_data_qs}

    # Prepare selling counts aligned with months labels (fill 0 if no data)
    selling_counts = [selling_data.get(month, 0) for month in months]

    # Similarly for orders
    order_data_qs = (
        OrderDetail.objects
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    order_data = {item['month'].strftime("%b %Y"): item['count'] for item in order_data_qs}
    order_counts = [order_data.get(month, 0) for month in months]

    context = {
        **(extra_context or {}),
        'total_selling': total_selling,
        'total_buying': total_buying,
        'total_payments': total_payments,
        'total_orders': total_orders,
        'months': months,
        'selling_counts': selling_counts,
        'order_counts': order_counts,
        # your existing latest records too if needed
    }
    return TemplateResponse(request, "admin/custom_index.html", context)