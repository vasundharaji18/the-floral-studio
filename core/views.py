from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth import logout, login
import json
import razorpay
from decimal import Decimal
import random
import string
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from razorpay.errors import SignatureVerificationError

# Import all your models and forms here
from .admin_views import admin_dashboard
from .models import (
    SiteSettings, NavLink, HeroSlide, Product, ProductCategory,
    SecondaryHero, FooterLink, SocialLink, Event, Footer, CartItem,
    Order, OrderItem, Payment, Invoice,
    Carpet, GreenWall, SportsProduct, ArtificialPlant, ContactMessage,
    AboutPage, Address
)
from .forms import CustomSignupForm, AddressForm
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings


# ======================
# HOME VIEW
# ======================
def home(request):
    cart_items_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
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
        'footer': Footer.objects.first(),
        'cart_items_count': cart_items_count,
    }
    return render(request, 'core/base.html', context)


# ======================
# CART MANAGEMENT
# ======================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "🛒 Item added to cart!")
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    delivery_charge = 50 if total > 0 else 0
    grand_total = total + delivery_charge

    order, created = Order.objects.get_or_create(user=request.user, status='pending')

    for item in cart_items:
        order_item, _ = OrderItem.objects.get_or_create(order=order, product=item.product)
        if order_item.quantity != item.quantity:
            order_item.quantity = item.quantity
            order_item.save()

    context = {
        'cart_items': cart_items,
        'total': total,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'order': order
    }
    return render(request, 'cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, user=request.user).delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_view')

@require_POST
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    action = request.POST.get('action')
    if action == 'increment':
        cart_item.quantity += 1
    elif action == 'decrement' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('cart_view')

# ======================
# HELPER FUNCTIONS
# ======================
def compute_order_total(order):
    return sum(item.product.price * item.quantity for item in order.items.all())

def generate_invoice_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def create_invoice_for_order(order):
    if hasattr(order, 'invoice'):
        return order.invoice
    total_amount = sum(item.total_price for item in order.items.all())
    tax = total_amount * Decimal('0.10')
    return Invoice.objects.create(
        order=order,
        invoice_number=generate_invoice_number(),
        billing_address=order.address,
        total_amount=total_amount + tax,
        tax=tax,
    )

# ======================
# CHECKOUT AND PAYMENT
# ======================
@login_required
def checkout_address(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.items.exists():
        messages.error(request, "Your cart is empty. Please add items before proceeding to checkout.")
        return redirect('cart_view')

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            order.delivery_address = address
            order.save()
            messages.success(request, "Address saved successfully. Proceeding to payment.")
            return redirect('checkout_payment', order_id=order.id)
    else:
        initial_data = {}
        if hasattr(request.user, 'address_set') and request.user.address_set.exists():
            last_address = request.user.address_set.last()
            initial_data = {
                'full_name': last_address.full_name,
                'phone_number': last_address.phone_number,
                'street_address': last_address.street_address,
                'city': last_address.city,
                'state': last_address.state,
                'pincode': last_address.pincode,
                'country': last_address.country,
            }
        form = AddressForm(initial=initial_data)

    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'checkout_address.html', context)

@login_required
def checkout_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check delivery address
    if not order.delivery_address:
        messages.error(request, "Please enter your delivery address first.")
        return redirect('checkout_address', order_id=order.id)

    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in order.items.all())
    delivery_charge = 50
    grand_total = subtotal + delivery_charge
    amount_in_paise = int(grand_total * 100)  # Razorpay expects paise

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "payment_capture": 1
        })

        # Always create a new Payment record for this attempt
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=grand_total,
            razorpay_order_id=razorpay_order['id'],
            status='created'
        )

    except Exception as e:
        messages.error(request, f"Payment gateway error: {str(e)}")
        return redirect('checkout_address', order_id=order.id)

    # Pass data to template
    context = {
        "order": order,
        "total": subtotal,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "user_email": request.user.email or "",
        "user_phone": getattr(getattr(request.user, 'profile', None), 'phone_number', "")
    }
    return render(request, "checkout_payment.html", context)

# ======================
# PAYMENT CALLBACKS
# ======================
@login_required
def payment_success(request):
    return render(request, "core/payment_success.html", {
        'order_id': request.GET.get('order_id'),
        'amount': request.GET.get('amount'),
        'payment_id': request.GET.get('payment_id'),
    })

def payment_failed(request):
    return render(request, "registration/payment_failed.html", {"order_id": request.GET.get('order_id')})

@csrf_exempt
def payment_verify(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=405)
    
    data = json.loads(request.body.decode("utf-8"))
    params_dict = {
        'razorpay_order_id': data.get('razorpay_order_id'),
        'razorpay_payment_id': data.get('razorpay_payment_id'),
        'razorpay_signature': data.get('razorpay_signature'),
    }
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(params_dict)
    except SignatureVerificationError as e:
        return JsonResponse({"status": "failed", "reason": "signature verification failed", "error_details": str(e)}, status=400)
    payment = get_object_or_404(Payment, razorpay_order_id=data.get('razorpay_order_id'))
    payment.status = 'paid'
    payment.razorpay_payment_id = data.get('razorpay_payment_id')
    payment.razorpay_signature = data.get('razorpay_signature')
    payment.raw_response = data
    payment.save()
    order = payment.order
    order.status = 'paid'
    order.save()
    create_invoice_for_order(order)
    CartItem.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "success"})


@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_WEBHOOK_SECRET)
    except SignatureVerificationError:
        return HttpResponseForbidden("Invalid signature")
    event_json = json.loads(payload.decode('utf-8'))
    event = event_json.get('event')
    payment_data = event_json.get('payload', {}).get('payment', {}).get('entity', {})
    order_id = payment_data.get('order_id')
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
        payment.status = 'paid' if event in ['payment.captured', 'payment.authorized'] else 'failed'
        payment.raw_response = payment_data
        payment.save()
    except Payment.DoesNotExist:
        pass
    return HttpResponse(status=200)

# ======================
# INVOICE AND PDF
# ======================
@login_required
def invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'core/invoice.html', {
        'order': order,
        'items': order.items.all(),
        'total': sum(item.total_price for item in order.items.all()),
    })

@login_required
def invoice_pdf_view(request, order_id):
    return HttpResponse("PDF generation temporarily disabled due to missing dependencies.")

# ======================
# USER MANAGEMENT
# ======================
def custom_logout(request):
    logout(request)
    messages.success(request, "👋 Logged out successfully.")
    return redirect('home')

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
        request.user.username = request.POST.get('username')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'core/edit_profile.html')

# ======================
# PRODUCT VIEWS
# ======================
def carpet_view(request):
    page_obj = Paginator(Carpet.objects.all(), 6).get_page(request.GET.get('page'))
    return render(request, 'core/carpet.html', {'page_obj': page_obj})

def greenwalls_view(request):
    page_obj = Paginator(GreenWall.objects.all().order_by('-id'), 6).get_page(request.GET.get('page'))
    return render(request, 'core/greenwalls.html', {'page_obj': page_obj})

def sports_view(request):
    page_obj = Paginator(SportsProduct.objects.all(), 6).get_page(request.GET.get('page'))
    return render(request, 'core/sports.html', {'page_obj': page_obj})

def artificial_plants_view(request):
    page_obj = Paginator(ArtificialPlant.objects.all(), 6).get_page(request.GET.get('page'))
    return render(request, 'artificial_plants.html', {'products': page_obj})

# ======================
# STATIC PAGES
# ======================
def about_view(request):
    return render(request, 'about.html', {'about': AboutPage.objects.first()})

def contact_view(request):
    if request.method == 'POST':
        name, email, message_text = request.POST.get('name'), request.POST.get('email'), request.POST.get('message')
        if name and email and message_text:
            ContactMessage.objects.create(name=name, email=email, message=message_text)
            messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
            return redirect('contact')
        messages.error(request, "Please fill all fields.")
    return render(request, 'contact.html')


# ======================
# BARCODE GENERATION
# ======================
def generate_barcode(request, code="123456789012"):
    ean = barcode.get_barcode_class('ean13')(code, writer=ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)
    return HttpResponse(buffer.getvalue(), content_type='image/png')


# ======================
# ADMIN ACCESS
# ======================
@login_required
def access_floral_admin(request):
    return redirect('/admin/')

def order_success(request):
    return render(request, 'order_success.html')



def search_view(request):
    query = request.GET.get('q')
    results = []
    if query:
        # Filter products where the name or description contains the query
        results = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query)
        # You can add more fields to search on if you want

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_results.html', context)



def product_detail_view(request, pk):
    """
    Retrieves and displays a single product's details.
    """
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product
    }
    return render(request, 'cart.html', context)