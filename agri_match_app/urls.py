from django.urls import path
from . import views  # Import your views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('about_us/', views.about_us, name='about_us'),  # About Us page
    path('contact_us/', views.contact_us, name='contact_us'),  # Contact Us page

    # Machinery-related pages
    path('machinery_listings/', views.machinery_listings, name='machinery_listings'),
    path('create_machinery_listing/', views.create_machinery_listing, name='create_machinery_listing'),

    # Operator-related pages
    path('operator_listings/', views.operator_listings, name='operator_listings'),
    path('create_operator_listing/', views.create_operator_listing, name='create_operator_listing'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('add_to_wishlist/<int:listing_id>/', views.add_to_wishlist, name='add_to_wishlist'),
]
