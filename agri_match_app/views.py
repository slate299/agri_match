from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from allauth.account.forms import SignupForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .models import CustomUser, MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review
from .forms import ReviewForm, MachineryListingForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'registration/account_login.html', {'form': form})

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful signup
    else:
        form = SignupForm()
    return render(request, 'registration/account_signup.html', {'form': form})

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
    if request.method == 'POST':
        form = MachineryListingForm(request.POST, request.FILES)
        if form.is_valid():
            machinery = form.save(commit=False)
            machinery.user = request.user
            machinery.save()
            return redirect('home')  # Redirect to a success page or listings page
    else:
        form = MachineryListingForm()

    return render(request, 'create_machinery_listing.html', {'form': form})


# Create operator listing (only for logged-in users)
@login_required
def create_machinery_listing(request):
    if request.method == 'POST':
        form = MachineryListingForm(request.POST, request.FILES)
        if form.is_valid():
            machinery = form.save(commit=False)
            machinery.user = request.user
            machinery.save()
            return redirect('home')  # Redirect to a success page or listings page
    else:
        form = MachineryListingForm()

    return render(request, 'create_machinery_listing.html', {'form': form})
# Add machinery listing to wishlist
@login_required
def add_to_wishlist(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.items.add(listing)
    messages.success(request, f'{listing.make} {listing.model} has been added to your wishlist!')
    return redirect('machinery_listings')

# View wishlist
@login_required
def view_wishlist(request):
    wishlist = Wishlist.objects.get(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

# Rent machinery or hire operator (only for logged-in users)
@login_required
def rent_or_hire(request, listing_id):
    listing = get_object_or_404(MachineryListing, pk=listing_id)
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        rental_days = (end_date - start_date).days
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
        user=request.user,
        machinery=listing if listing_type == 'machinery' else None,
        operator=listing if listing_type == 'operator' else None
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            if listing_type == 'machinery':
                review.machinery = listing
            else:
                review.operator = listing
            review.save()
            return redirect('listing_detail', listing_id=listing.id, listing_type=listing_type)
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'listing': listing, 'existing_review': existing_review})

# Custom Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/account_password_reset.html'
    email_template_name = 'registration/password_reset_email.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        response['Location'] = self.success_url
        return response

    success_url = '/password_reset_done/'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/account_password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Password reset done view
def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')

# Admin Dashboard (Only accessible to superusers)
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")

    machinery_count = MachineryListing.objects.count()
    operator_count = OperatorListing.objects.count()
    user_count = CustomUser.objects.count()
    rental_count = RentalTransaction.objects.count()

    return render(request, 'admin_dashboard.html', {
        'machinery_count': machinery_count,
        'operator_count': operator_count,
        'user_count': user_count,
        'rental_count': rental_count
    })

# View for displaying all machinery listings
def machinery_listings(request):
    machinery_list = MachineryListing.objects.filter(listing_type='machinery')
    return render(request, 'machinery_listings.html', {'machinery_list': machinery_list})

# View for displaying all operator listings
def operator_listings(request):
    operator_list = OperatorListing.objects.filter(listing_type='operator')
    return render(request, 'operator_listings.html', {'operator_list': operator_list})