from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils import timezone

# Custom User Model
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_machinery_lister = models.BooleanField(default=False)
    is_operator_lister = models.BooleanField(default=False)
    is_renter = models.BooleanField(default=False)

    # Override the related_name for groups and user_permissions to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Custom related name to avoid conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Custom related name to avoid conflict
        blank=True
    )

    def __str__(self):
        return self.username


# New Machinery Category Model
class MachineryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MachineryType(models.Model):
    category = models.ForeignKey(MachineryCategory, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

# Updated Machinery Listing Model with Location
class MachineryListing(models.Model):
    category = models.ForeignKey(MachineryCategory, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey(MachineryType, on_delete=models.SET_NULL, null=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    condition = models.CharField(
        max_length=100,
        choices=[('New', 'New'), ('Used', 'Used')],
        default='New'
    )
    description = models.TextField()
    image = models.ImageField(upload_to='machinery/', blank=True, null=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)  # New location field
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='machinery_listings')

    def clean(self):
        if self.available_to and self.available_from and self.available_to < self.available_from:
            raise ValidationError("Available to date must be after available from date.")

    def __str__(self):
        return f"{self.make} {self.model} ({self.category.name})"


# Operator Listing Model (Updated)
class OperatorListing(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    certification = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    profile_picture = models.ImageField(upload_to='operators/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Contact details field
    email = models.EmailField(max_length=255, blank=True, null=True)  # Contact details field
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operator_listings')

    def clean(self):
        if self.available_to and self.available_from and self.available_to < self.available_from:
            raise ValidationError("Available to date must be after available from date.")

    def save(self, *args, **kwargs):
        # Automatically assign the user if not already set
        if not self.user:
            raise ValidationError("User must be assigned to the listing")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# Wishlist Model
class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    items = models.ManyToManyField(
        MachineryListing,
        blank=True,
        verbose_name="Wishlist Items"
        )

    def __str__(self):
        return f"Wishlist for {self.user.username}"

    def item_count(self):
        return self.items.count()


# Rental Transaction Model
class RentalTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rental_transactions')
    machinery = models.ForeignKey(MachineryListing, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    operator = models.ForeignKey(OperatorListing, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Rental Transaction for {self.user.username}"


# Updated Review model
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    machinery = models.ForeignKey(MachineryListing, null=True, blank=True, on_delete=models.CASCADE)
    operator = models.ForeignKey(OperatorListing, null=True, blank=True, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Review by {self.user.username} for {self.content_type.model} {self.object_id}"

