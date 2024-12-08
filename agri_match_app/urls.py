from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='account_login'),
    path('signup/', views.signup_view, name='account_signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Home and about pages
    path('', views.home, name='home'),
    path('about_us/', views.about_us, name='about_us'),

    # Contact Us pages
    path('contact_us/', views.contact_us, name='contact_us'),
    path('contact_us/thankyou/', views.contact_us_thankyou, name='contact_us_thankyou'),

    # Listings
    path('machinery_listings/', views.machinery_listings, name='machinery_listings'),
    path('operator_listings/', views.operator_listings, name='operator_listings'),

    # Create listings (only for logged-in users)
    path('create_machinery_listing/', views.create_machinery_listing, name='create_machinery_listing'),
    path('create_operator_listing/', views.create_operator_listing, name='create_operator_listing'),

    # Add to wishlist
    path('add_to_wishlist/<int:listing_id>/', views.add_to_wishlist, name='add_to_wishlist'),

    # Wishlist view
    path('wishlist/', views.wishlist, name='wishlist'),

    # Rent or hire machinery or operators
    path('rent_or_hire/<int:listing_id>/', views.rent_or_hire, name='rent_or_hire'),

    # Reviews
    path('submit_review/<int:listing_id>/<str:listing_type>/', views.submit_review, name='submit_review'),

    # Password Reset
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    # Admin Dashboard (Only for superusers)
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('get-types/<int:category_id>/', views.get_types, name='get_types'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
]