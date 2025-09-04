# core/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from core import admin_views
from . import views

urlpatterns = [
    # 🏠 Home page & static pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Password Reset Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # 🛒 Cart functionality
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),

    # 💳 Checkout & Payment
    path('checkout/address/<int:order_id>/', views.checkout_address, name='checkout_address'),
    path('checkout/payment/<int:order_id>/', views.checkout_payment, name='checkout_payment'),
    path('order-success/', views.order_success, name='order_success'),
    
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('razorpay/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    
    # Products (Streamlined)
    path('carpets/', views.carpet_view, name='carpet_view'),
    path('greenwalls/', views.greenwalls_view, name='greenwalls_view'),
    path('sports/', views.sports_view, name='sports_view'),
    path('artificial-plants/', views.artificial_plants_view, name='artificial_plants_view'),
    
    # Invoice view
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice_view'),

    # Admin dashboard
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path("access-admin/", views.access_floral_admin, name="access_floral_admin"),

     path('search/', views.search_view, name='search'),

     path('products/<int:pk>/', views.product_detail_view, name='product_detail')
]