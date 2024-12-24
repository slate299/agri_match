from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('operator/<int:listing_id>/', views.operator_listing_details, name='operator_listing_details'),
    # Add to wishlist
    path('add_to_wishlist/<int:listing_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:listing_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    # Wishlist view
    path('wishlist/', views.wishlist, name='wishlist'),

    # Rent or hire machinery or operators
    path('rent-item/<int:listing_id>/', views.rent_or_hire, name='rent_item'),
    path('rental-success/', views.rental_success, name='rental_success'),
    path('get-machinery-types/<int:category_id>/', views.get_machinery_types, name='get_machinery_types'),
    # Reviews
    path('machinery/<int:listing_id>/review/', views.add_review, {'listing_type': 'machinery'}, name='add_machinery_review'),
    path('operator/<int:listing_id>/review/', views.add_review, {'listing_type': 'operator'}, name='add_operator_review'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('register-role/', views.register_role, name='register_role'),
    path('get-machinery-types/<int:category_id>/', views.get_machinery_types, name='get-machinery-types'),
    path('machinery/<int:id>/', views.machinery_listing_detail, name='machinery_listing_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)