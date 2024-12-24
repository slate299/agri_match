from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review, MachineryCategory, \
    MachineryType
from .forms import ReviewForm, MachineryListingForm, OperatorListingForm, RoleRegistrationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Avg
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from .signals import assign_user_group


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

        # Send email to admin
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
            return redirect('machinery_listings')
    else:
        form = MachineryListingForm()

    return render(request, 'create_machinery_listing.html', {'form': form})


@login_required
def create_operator_listing(request):
    # Restrict access to specific groups
    if not request.user.groups.filter(name__in=["Operator Lister", "Admin"]).exists():
        return HttpResponseForbidden('You do not have permission to create an operator listing.')

    if request.method == 'POST':
        form = OperatorListingForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but do not commit to database yet
            operator = form.save(commit=False)

            # Assign the logged-in user to the operator listing
            operator.user = request.user

            # Save the instance to the database
            operator.save()

            # Add a success message to inform the user of the successful listing creation
            messages.success(request, "Operator listing created successfully!")

            return redirect('home')  # Redirect to home page after successful creation
        else:
            # Optionally, you can display form errors in the template
            print(f"Form errors: {form.errors}")  # This is for debugging, can be removed in production

    else:
        form = OperatorListingForm()

    return render(request, 'create_operator_listing.html', {'form': form})


# Add machinery listing to wishlist
@login_required
def add_to_wishlist(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

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
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    machinery_in_wishlist = wishlist.items.all()

    return render(request, 'wishlist.html', {'wishlist': machinery_in_wishlist})


@login_required
def rent_or_hire(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    if request.method == 'POST':
        # Parse dates from the POST request
        try:
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('rent_or_hire', listing_id=listing_id)

        # Validate date range
        if start_date > end_date:
            messages.error(request, "The rental start date cannot be after the end date.")
            return redirect('rent_or_hire', listing_id=listing_id)

        # Calculate rental period and total amount
        rental_days = (end_date - start_date).days
        if rental_days < 1:
            messages.error(request, "The rental period must be at least one day.")
            return redirect('rent_or_hire', listing_id=listing_id)

        total_amount = listing.price_per_day * rental_days

        # Create a rental transaction
        RentalTransaction.objects.create(
            user=request.user,
            machinery=listing,
            rental_start_date=start_date,
            rental_end_date=end_date,
            total_amount=total_amount
        )

        # Success message or response
        messages.success(request, "Rental request submitted successfully.")
        return redirect('rental_success')  # Redirect to the success page by its URL name

    return render(request, 'rent_or_hire.html', {'listing': listing})

def rental_success(request):
    return render(request, 'rental_success.html')

# Machinery Listing Detail View
def machinery_listing_detail(request, id):
    # Get the specific machinery listing or return 404 if not found
    listing = get_object_or_404(MachineryListing, id=id)

    # Get the content_type for MachineryListing
    machinery_content_type = ContentType.objects.get_for_model(MachineryListing)

    # Get all reviews for this machinery listing
    reviews = Review.objects.filter(content_type=machinery_content_type, object_id=listing.id)

    return render(request, 'machinery_listing_details.html', {
        'listing': listing,
        'reviews': reviews,
    })


# Operator Listing Detail View
def operator_listing_details(request, listing_id):
    # Get the specific operator listing or return 404 if not found
    operator_listing = get_object_or_404(OperatorListing, id=listing_id)

    # Get the content_type for OperatorListing
    operator_content_type = ContentType.objects.get_for_model(OperatorListing)

    # Get all reviews for this operator listing
    reviews = Review.objects.filter(content_type=operator_content_type, object_id=operator_listing.id)

    return render(request, 'operator_listing_details.html', {
        'operator_listing': operator_listing,
        'reviews': reviews,
    })


# Add review for machinery or operator listing
@login_required
def add_review(request, listing_id, listing_type):
    # Fetch the specific listing object based on type
    if listing_type == 'machinery':
        listing = get_object_or_404(MachineryListing, id=listing_id)
    elif listing_type == 'operator':
        listing = get_object_or_404(OperatorListing, id=listing_id)
    else:
        return redirect('home')  # Redirect if invalid listing type

    # Check if the user has already reviewed the listing
    content_type = ContentType.objects.get_for_model(listing)
    existing_review = Review.objects.filter(user=request.user, content_type=content_type, object_id=listing.id).first()

    if existing_review:
        return redirect('machinery_listing_detail', id=listing.id) if listing_type == 'machinery' else redirect('operator_listing_detail', id=listing.id)

    # Handle form submission
    if request.method == 'POST':
        form = ReviewForm(request.POST, content_object=listing)
        if form.is_valid():
            # Save the form but do not commit to database yet
            review = form.save(commit=False)

            # Manually assign the user to the review
            review.user = request.user

            # Assign content_type and object_id to the review
            review.content_type = content_type
            review.object_id = listing.id

            # Save the review instance to the database
            review.save()

            # Add a success message to inform the user of the successful review submission
            messages.success(request, "Review submitted successfully!")

            # Redirect to the listing details page after submission
            return redirect('machinery_listing_detail', id=listing.id) if listing_type == 'machinery' else redirect('operator_listing_detail', id=listing.id)

        else:
            # Optionally, you can print errors if form is invalid
            print("Form errors:", form.errors)
    else:
        form = ReviewForm(content_object=listing)

    return render(request, 'add_review.html', {
        'form': form,
        'listing': listing,
    })



# Machinery Listing View
def machinery_listings(request):
    machinery_list = MachineryListing.objects.all()
    paginator = Paginator(machinery_list, 10)
    page = request.GET.get('page')

    try:
        machinery_listings = paginator.page(page)
    except PageNotAnInteger:
        machinery_listings = paginator.page(1)
    except EmptyPage:
        machinery_listings = paginator.page(paginator.num_pages)

    return render(request, 'machinery_listings.html', {'machinery_listings': machinery_listings})


# Operator Listing View
def operator_listings(request):
    operator_list = OperatorListing.objects.all()
    print(operator_list)
    paginator = Paginator(operator_list, 9)
    page = request.GET.get('page')

    try:
        operator_listings_paginated = paginator.page(page)
    except PageNotAnInteger:
        operator_listings_paginated = paginator.page(1)
    except EmptyPage:
        operator_listings_paginated = paginator.page(paginator.num_pages)

    return render(request, 'operator_listings.html', {'operator_listings': operator_listings_paginated})


# Privacy Policy View
def privacy_policy(request):
    return render(request, 'privacy_policy.html')


# Terms & Conditions View
def terms_conditions(request):
    return render(request, 'terms_conditions.html')

# Remove machinery listing from wishlist
@login_required
def remove_from_wishlist(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if listing in wishlist.items.all():
        wishlist.items.remove(listing)
        messages.success(request, f'{listing.make} {listing.model} has been removed from your wishlist!')
    else:
        messages.error(request, f'{listing.make} {listing.model} is not in your wishlist.')

    return redirect('wishlist')

# Function to fetch machinery types based on the selected category
def get_machinery_types(request, category_id):
    # Get the selected category object
    category = get_object_or_404(MachineryCategory, id=category_id)
    # Get the associated machinery types
    machinery_types = MachineryType.objects.filter(category=category)
    # Serialize the machinery types to send to the template
    types_data = list(machinery_types.values('id', 'name'))
    return JsonResponse({'types': types_data})  # Changed key to 'types'

@login_required
def register_role(request):
    if request.method == 'POST':
        form = RoleRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            user = request.user
            if role == 'machinery_lister':
                user.is_machinery_lister = True
            elif role == 'operator_lister':
                user.is_operator_lister = True
            elif role == 'renter':
                user.is_renter = True
            user.save()

            # Manually trigger the signal's group assignment function
            assign_user_group(sender=CustomUser, instance=user, created=False)

            return redirect('home')
    else:
        form = RoleRegistrationForm()

    return render(request, 'register_role.html', {'form': form})
