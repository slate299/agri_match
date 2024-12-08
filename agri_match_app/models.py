from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

# Custom User Model
class CustomUser(AbstractUser):
    is_lister = models.BooleanField(default=False)
    is_renter = models.BooleanField(default=False)
    is_wishlist_user = models.BooleanField(default=True)

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
    category = models.ForeignKey(MachineryCategory, on_delete=models.SET_NULL, null=True)
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

    def __str__(self):
        return f"{self.make} {self.model} ({self.category.name})"


# Operator Listing Model
class OperatorListing(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    certification = models.CharField(max_length=255)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    profile_picture = models.ImageField(upload_to='operators/', blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='operator_listings')

    def __str__(self):
        return self.name


# Wishlist Model
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlists')
    items = models.ManyToManyField(MachineryListing, blank=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"


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


# Review Model
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    operator = models.ForeignKey(OperatorListing, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    machinery = models.ForeignKey(MachineryListing, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.PositiveIntegerField(default=1, choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.operator if self.operator else self.machinery}"