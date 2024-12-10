from django.urls import path
from . import views


urlpatterns = [

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
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('register-role/', views.register_role, name='register_role'),

]