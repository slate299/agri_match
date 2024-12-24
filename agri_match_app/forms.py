from django import forms
from .models import (MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review,
                     CustomUser, MachineryCategory, MachineryType)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Custom User Registration Form (Sign Up)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    group_name = forms.ChoiceField(
        choices=[('Admin', 'Admin'),
                 ('Machinery Lister', 'Machinery Lister'),
                 ('Operator Lister', 'Operator Lister'),
                 ('Renter', 'Renter')],
        label="Choose your role",
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'group_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set default user values or roles if needed
        if commit:
            user.save()

        # Assign the user to the appropriate group based on their role choice
        group_name = self.cleaned_data['group_name']
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

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
    name = forms.CharField(
        max_length=255,
        label="Operator's Full Name",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Provide a brief bio of the operator'}),
        required=True,
        label="Bio"
    )

    certification = forms.CharField(
        max_length=255,
        label="Certification",
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'List any certifications held by the operator'}),
        required=False
    )

    hourly_rate = forms.DecimalField(
        label="Hourly Rate",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        required=True
    )

    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message='Phone number must be valid.')],
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False
    )

    available_from = forms.DateField(
        label="Available From",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    available_to = forms.DateField(
        label="Available To",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    profile_picture = forms.ImageField(
        label="Profile Picture",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    class Meta:
        model = OperatorListing
        fields = ['name', 'bio', 'certification', 'hourly_rate', 'available_from', 'available_to', 'profile_picture',
                  'phone_number', 'email']

    def save(self, commit=True):
        operator = super().save(commit=False)
        # Associate with the current logged-in user
        operator.user = self.initial.get('user')
        if commit:
            operator.save()
        return operator

    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get("available_from")
        available_to = cleaned_data.get("available_to")

        if available_from and available_to and available_from > available_to:
            raise ValidationError("Available From date cannot be later than Available To date.")

        return cleaned_data



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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'content_type', 'object_id']  # Include relevant fields for GenericForeignKey
        widgets = {
            'rating': forms.Select(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'})
        }

    def __init__(self, *args, **kwargs):
        self.user = None
        content_object = kwargs.pop('content_object', None)
        super().__init__(*args, **kwargs)

        if content_object:
            # Set content_type and object_id dynamically based on the content_object passed
            content_type = ContentType.objects.get_for_model(content_object)
            self.fields['content_type'].initial = content_type
            self.fields['object_id'].initial = content_object.id

    def save(self, commit=True):
        review = super().save(commit=False)
        review.user = self.user  # Associate with the current logged-in user
        if commit:
            review.save()
        return review


class RoleRegistrationForm(forms.Form):
    ROLE_CHOICES = [
        ('machinery_lister', 'Machinery Lister'),
        ('operator_lister', 'Operator Lister'),
        ('renter', 'Renter'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

