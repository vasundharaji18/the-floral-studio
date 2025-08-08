# core/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import signup_view
from django.contrib.auth.views import LogoutView

from core import views as core_views

from .views import subscribe_newsletter

urlpatterns = [
    # 🏠 Home page
    path('', views.home, name='home'),

    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     # Forget Password Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    # 🛒 Cart functionality
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),

    # 💳 Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

#product
    path('carpet/', views.carpet_page, name='carpet'),
    path('carpets/', views.carpet_view, name='carpet_view'),
    path('carpets/', views.carpet_list, name='carpet_list'),

    path('greenwalls/', views.greenwalls_view, name='greenwalls_view'),

    path('sports/', core_views.sports_view, name='sports_view'),


   path('artificialplants/', views.artificial_plants_view, name='artificialplants_view'),
   path('artificial-plants/', views.artificial_plants_view, name='artificial_plants'),
   
       path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
]
