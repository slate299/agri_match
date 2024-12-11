from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review, MachineryType
from .forms import ReviewForm, MachineryListingForm, OperatorListingForm, CustomUserCreationForm, RoleRegistrationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.urls import reverse_lazy


# Home view
def home(request):
    listings = MachineryListing.objects.all()
    operators = OperatorListing.objects.all()
    return render(request, 'home.html', {'listings': listings, 'operators': operators})

# About Us view
def about_us(request):
    return render(request, 'about_us.html')

# Contact Us view
def contact_us(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        phone = request.POST.get('phone', '')

        # Send email to admin (or store the contact info in the database)
        send_mail(
            f"Contact Us Message from {name}",
            f"Message: {message}\nPhone: {phone}",
            email,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return redirect('contact_us_thankyou')

    return render(request, 'contact_us.html')

# Contact Us Thank You view
def contact_us_thankyou(request):
    return render(request, 'contact_us_thankyou.html')

# Create machinery listing (only for logged-in users)
@login_required
def create_machinery_listing(request):
    if not request.user.groups.filter(name__in=["Machinery Lister", "Admin"]).exists():
        return HttpResponseForbidden("You are not authorized to create a machinery listing.")
    if request.method == 'POST':
        form = MachineryListingForm(request.POST, request.FILES)
        if form.is_valid():
            machinery = form.save(commit=False)
            machinery.user = request.user  # Ensure the user is assigned to the listing
            machinery.save()
            return redirect('machinery_listings')  # Redirect to a success page or listings page
    else:
        form = MachineryListingForm()
        print(form.errors)
    return render(request, 'create_machinery_listing.html', {'form': form})

# Create operator listing
@login_required
def create_operator_listing(request):
    if request.method == 'POST':
        form = OperatorListingForm(request.POST, request.FILES)
        if form.is_valid():
            operator = form.save(commit=False)
            operator.user = request.user  # Ensure the user is assigned to the listing
            operator.save()
            return redirect('home')
    else:
        form = OperatorListingForm()
        print(form.errors)
    return render(request, 'create_operator_listing.html', {'form': form})


# Add machinery listing to wishlist
@login_required
def add_to_wishlist(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Add or remove item based on its presence
    if listing in wishlist.items.all():
        wishlist.items.remove(listing)
        messages.success(request, f'{listing.make} {listing.model} has been removed from your wishlist!')
    else:
        wishlist.items.add(listing)
        messages.success(request, f'{listing.make} {listing.model} has been added to your wishlist!')

    return redirect('machinery_listings')


# View the user's wishlist
@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)  # Reference CustomUser here
    # Get the items (machinery listings) in the wishlist
    machinery_in_wishlist = wishlist.items.all()

    return render(request, 'wishlist.html', {'wishlist': machinery_in_wishlist})

# Rent machinery or hire operator (only for logged-in users)
@login_required
def rent_or_hire(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        if start_date > end_date:
            messages.error(request, "The rental start date cannot be after the end date.")
            return redirect('rent_or_hire', listing_id=listing_id)

        rental_days = (end_date - start_date).days
        if rental_days < 1:
            messages.error(request, "The rental period must be at least one day.")
            return redirect('rent_or_hire', listing_id=listing_id)

        total_amount = listing.price_per_day * rental_days
        RentalTransaction.objects.create(
            user=request.user,
            machinery=listing,
            rental_start_date=start_date,
            rental_end_date=end_date,
            total_amount=total_amount
        )
        return HttpResponse('Rental request submitted')
    return render(request, 'rent_or_hire.html', {'listing': listing})


# Submit review for a machinery or operator
@login_required
def submit_review(request, listing_id, listing_type):
    if listing_type == 'machinery':
        listing = get_object_or_404(MachineryListing, pk=listing_id)
    elif listing_type == 'operator':
        listing = get_object_or_404(OperatorListing, pk=listing_id)
    else:
        return HttpResponse("Invalid listing type.", status=400)

    # Check if the user has already reviewed this listing
    existing_review = Review.objects.filter(
        user=request.user,  # Reference CustomUser here
        machinery=listing if listing_type == 'machinery' else None,
        operator=listing if listing_type == 'operator' else None
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user  # Reference CustomUser here
            if listing_type == 'machinery':
                review.machinery = listing
            else:
                review.operator = listing
            review.save()
            return redirect('listing_detail', listing_id=listing.id, listing_type=listing_type)
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'listing': listing, 'existing_review': existing_review})


# View for displaying all machinery listings
def machinery_listings(request):
    machinery_list = MachineryListing.objects.all()  # No need for listing_type
    return render(request, 'machinery_listings.html', {'machinery_list': machinery_list})

# View for displaying all operator listings
def operator_listings(request):
    operator_list = OperatorListing.objects.all()  # No need for listing_type
    return render(request, 'operator_listings.html', {'operator_list': operator_list})

def get_machinery_types(request, category_id):
    types = MachineryType.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'types': list(types)}, safe=False)

# Privacy Policy View
def privacy_policy(request):
    return render(request, 'privacy_policy.html')

# Terms & Conditions View
def terms_conditions(request):
    return render(request, 'terms_conditions.html')

@login_required
def register_role(request):
    if request.method == 'POST':
        form = RoleRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']

            # Update the user's role based on the selection
            user = request.user
            if role == 'machinery_lister':
                user.is_machinery_lister = True
            elif role == 'operator_lister':
                user.is_operator_lister = True
            elif role == 'renter':
                user.is_renter = True

            user.save()

            # Redirect to a success or home page
            return redirect('home')
    else:
        form = RoleRegistrationForm()

    return render(request, 'register_role.html', {'form': form})

# Create user groups automatically when migrations are done (on app startup)
@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Create Admin group
    admin_group, created = Group.objects.get_or_create(name='Admin')

    # Create Machinery Lister group
    machinery_lister_group, created = Group.objects.get_or_create(name='Machinery Lister')

    # Create Operator Lister group
    operator_lister_group, created = Group.objects.get_or_create(name='Operator Lister')

    # Create Renter group
    renter_group, created = Group.objects.get_or_create(name='Renter')
