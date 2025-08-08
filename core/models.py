from django.db import models
from django.contrib.auth.models import User


def navbar_context(request):
    return {
        'navbar_logo': NavbarLogo.objects.all(),
        'navbar_menu_items': NavbarMenuItem.objects.all()
    }

def site_settings(request):
    settings = SiteSettings.objects.first()
    return {'site_settings': settings}

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="The Floral Studio")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return self.site_name

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

class NavbarLogo(models.Model):
    logo_image = models.ImageField(upload_to='navbar/logo/')

    def __str__(self):
        return "Navbar Logo"

class NavbarMenuItem(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="The Floral Studio")
    logo = models.ImageField(upload_to="logo/")
    primary_color = models.CharField(max_length=20, default="#2e7d32")  # green
    secondary_color = models.CharField(max_length=20, default="#ffffff")  # white
    text_color = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.site_name

class NavLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class HeroSlide(models.Model):
    image = models.ImageField(upload_to='hero/')
    headline = models.CharField(max_length=200)
    sub_text = models.TextField(blank=True, null=True)
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_link = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.headline

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.quantity * self.product.price



class Event(models.Model):
    image = models.ImageField(upload_to='events/')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class SubscribeSection(models.Model):
    text = models.TextField()
    placeholder = models.CharField(max_length=100, default="Enter your email")

    def __str__(self):
        return "Subscribe Section"

class Newsletter(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class FooterLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class SocialLink(models.Model):
    platform = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=100)  # e.g. "fab fa-instagram"
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.platform

class SecondaryHero(models.Model):
    image = models.ImageField(upload_to='secondary_hero/')
    heading = models.CharField(max_length=200)
    sub_text = models.TextField()

    def __str__(self):
        return self.heading


class Event(models.Model):
    image = models.ImageField(upload_to='events/')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


class NewsletterEmail(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Footer(models.Model):
    text = models.TextField(default="© 2025 The Floral Studio. All rights reserved.")
    background_color = models.CharField(max_length=20, default="#000000")
    text_color = models.CharField(max_length=20, default="#ffffff")
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Footer Settings"


class Order(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.product} x {self.quantity}"
    

def some_function():
    from .models import Product  # Safe import inside the function
    # Example usage
    products = Product.objects.all()
    for product in products:
        print(product.name)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"
#product

class CarpetProduct(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='carpets/')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
from django.db import models

class Carpet(models.Model):
    CATEGORY_CHOICES = [
        ('Wool', 'Wool'),
        ('Silk', 'Silk'),
        ('Cotton', 'Cotton'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='carpets/')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class GreenWall(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='greenwalls/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    
class SportsProduct(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='sports/')
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ArtificialPlant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='plants/')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.name
    




class BusinessProfile(models.Model):
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        
        ('others', 'Others'),
    ]

    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    tin = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, blank=True)
    business_address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    signature = models.ImageField(upload_to='business_signatures/', blank=True, null=True)

    def __str__(self):
        return self.business_name


class SellingDetail(models.Model):
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    sold_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} sold by {self.seller}"

class BuyingDetail(models.Model):
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    bought_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} bought by {self.buyer}"

class PaymentDetail(models.Model):
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment {self.order_id} - {self.payment_status}"

class OrderDetail(models.Model):
    order_number = models.CharField(max_length=100)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"