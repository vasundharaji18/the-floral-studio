from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import (
    SiteSettings, NavLink, HeroSlide, Product, ProductCategory,
    SecondaryHero, FooterLink, SocialLink, Event, Footer, CartItem
)
from .forms import NewsletterForm, OrderForm
from django.contrib.auth import login, authenticate, logout
from .forms import CustomSignupForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Newsletter

#product
from .models import CarpetProduct
from django.core.paginator import Paginator
from .models import Cart, CartItem 
from .models import Carpet
from .models import GreenWall
from .models import SportsProduct
from .models import ArtificialPlant

# ======================
# HOME VIEW
# ======================
def home(request):
    if request.method == 'POST' and 'subscribe' in request.POST:
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for subscribing!")
            return redirect('/')
    else:
        form = NewsletterForm()

    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(user=request.user).count()

    context = {
        'site': SiteSettings.objects.first(),
        'nav_links': NavLink.objects.all(),
        'hero_slides': HeroSlide.objects.all(),
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
        'secondary_hero': SecondaryHero.objects.first(),
        'footer_links': FooterLink.objects.all(),
        'social_links': SocialLink.objects.all(),
        'events': Event.objects.all(),
        'newsletter_form': form,
        'footer': Footer.objects.latest('id'),
        'cart_items_count': cart_items_count,
    }
    return render(request, 'core/base.html', context)

# ======================
# ADD TO CART VIEW
# ======================

def custom_logout(request):
    logout(request)
    messages.success(request, "\U0001F44B Logged out successfully.")
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "\U0001F6D2 Item added to cart!")
    return redirect('cart_view')

# ======================
# CART VIEW
# ======================
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_items_count': cart_items.count(),
    }
    return render(request, 'core/cart.html', context)

# ======================
# REMOVE FROM CART
# ======================
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_view')

# ======================
# UPDATE CART QUANTITY
# ======================
@require_POST
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increment':
            cart_item.quantity += 1
        elif action == 'decrement' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect('cart_view')

# ======================
# CHECKOUT
# ======================
@login_required
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            CartItem.objects.filter(user=request.user).delete()
            messages.success(request, "✅ Order placed successfully!")
            return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {'form': form})

# ======================
# ORDER SUCCESS
# ======================
@login_required
def order_success(request):
    return render(request, 'order_success.html')

# ======================
# SIGNUP VIEWS
# ======================
def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "✅ Signed up and logged in!")
            return redirect('home')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Account created successfully! Please log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'core/profile.html')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        request.user.username = username
        request.user.email = email
        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'edit_profile.html')

# ======================
# PRODUCT VIEWS
# ======================
def carpet_page(request):
    carpets = CarpetProduct.objects.filter(is_available=True)
    return render(request, 'carpet.html', {'carpets': carpets})

def carpet_view(request):
    carpets = Carpet.objects.all()
    paginator = Paginator(carpets, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'carpet.html', context)

def carpet_list(request):
    carpets = Carpet.objects.all()
    paginator = Paginator(carpets, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'carpet.html', {'page_obj': page_obj})

def greenwalls_view(request):
    greenwalls = GreenWall.objects.all().order_by('-id')
    paginator = Paginator(greenwalls, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/greenwalls.html', {'page_obj': page_obj})

def sports_view(request):
    products = SportsProduct.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/sports.html', {'page_obj': page_obj})

def artificial_plants_view(request):
    plants = ArtificialPlant.objects.all()
    paginator = Paginator(plants, 6)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'artificial_plants.html', {'products': products})

def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if email:
            if not Newsletter.objects.filter(email=email).exists():
                Newsletter.objects.create(email=email)
                messages.success(request, "✅ You've successfully subscribed to our newsletter!")
            else:
                messages.info(request, "You are already subscribed.")
        else:
            messages.error(request, "Please enter a valid email address.")

    return redirect(request.META.get("HTTP_REFERER", "/"))

