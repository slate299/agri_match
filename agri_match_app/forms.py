from django import forms
from .models import (MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review,
                     CustomUser, MachineryCategory, MachineryType)
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# Custom User Registration Form (Sign Up)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, request=None, commit=True):
        user = super().save(commit=False)
        user.is_lister = False  # Default to not being a lister
        user.is_renter = False  # Default to not being a renter
        user.is_wishlist_user = False  # Default to not being a wishlist user
        if request:
            pass
        if commit:
            user.save()
        return user

# Machinery Listing
class MachineryListingForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=MachineryCategory.objects.all(),
        label="Category",
        required=True
    )
    type = forms.ModelChoiceField(
        queryset=MachineryType.objects.none(),
        label="Type",
        required=True
    )
    condition = forms.ChoiceField(
        choices=[('New', 'New'), ('Used', 'Used')],
        label="Condition",
        required=True
    )
    availability = forms.ChoiceField(
        choices=[('Available Now', 'Available Now'), ('Available in 2 weeks', 'Available in 2 weeks'),
                 ('Available in 1 month', 'Available in 1 month')],
        label="Availability",
        required=True
    )
    location = forms.CharField(
        max_length=255,
        label="Location (County/Region)",
        required=False
    )
    category_of_service = forms.ChoiceField(
        choices=[('Renting Only', 'Renting Only'), ('Renting with Operator', 'Renting with Operator')],
        label="Category of Service",
        required=True
    )

    class Meta:
        model = MachineryListing
        fields = [
            'category', 'type', 'make', 'model', 'condition', 'availability', 'location', 'category_of_service',
            'description', 'price_per_day', 'available_from', 'available_to', 'image'
        ]
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['type'].queryset = MachineryType.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['type'].queryset = MachineryType.objects.none()
        elif self.instance.pk:
            self.fields['type'].queryset = self.instance.category.types.all()


# Operator Listing Form (For Listers to Add Operators)
class OperatorListingForm(forms.ModelForm):
    class Meta:
        model = OperatorListing
        fields = ['name', 'bio', 'certification', 'hourly_rate', 'available_from', 'available_to', 'profile_picture']

    def save(self, commit=True):
        operator = super().save(commit=False)
        operator.user = self.instance.user  # Associate with the current logged-in user
        if commit:
            operator.save()
        return operator


# Wishlist Form (For Users to Save Items to Wishlist)
class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['items']

    def save(self, commit=True):
        wishlist = super().save(commit=False)
        if not wishlist.user:
            wishlist.user = self.initial.get('user')  # Associate with the current logged-in user
        if commit:
            wishlist.save()
        return wishlist


# Rental Transaction Form (For Renters to Book Rentals)
class RentalTransactionForm(forms.ModelForm):
    class Meta:
        model = RentalTransaction
        fields = ['machinery', 'operator', 'rental_start_date', 'rental_end_date', 'total_amount']

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.user = self.instance.user  # Associate with the current logged-in user
        if commit:
            transaction.save()
        return transaction


# Review Form (For Users to Leave Reviews)
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['operator', 'machinery', 'rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'})
        }
    def save(self, commit=True):
        review = super().save(commit=False)
        review.user = self.instance.user  # Associate with the current logged-in user
        if commit:
            review.save()
        return review