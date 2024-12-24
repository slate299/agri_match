from django.contrib import admin
from .models import CustomUser, MachineryCategory, MachineryType, MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

# Register Custom User model with admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter', 'is_active', 'date_joined']
    list_filter = ['is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['date_joined']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter')}),  # Add custom fields
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter')}),  # Add custom fields
    )

# Register CustomUser with the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

# Unregister Group model if you don't want to use it with CustomUser
admin.site.unregister(Group)

# Register the MachineryCategory model
class MachineryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    ordering = ['name']

admin.site.register(MachineryCategory, MachineryCategoryAdmin)

# Register the MachineryType model
class MachineryTypeAdmin(admin.ModelAdmin):
    list_display = ['category', 'name']
    search_fields = ['name']
    list_filter = ['category']

admin.site.register(MachineryType, MachineryTypeAdmin)

# Register the MachineryListing model
class MachineryListingAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'category', 'type', 'price_per_day', 'available_from', 'available_to', 'location', 'user']
    list_filter = ['category', 'type', 'condition', 'user']
    search_fields = ['make', 'model', 'user__username']
    ordering = ['available_from']

admin.site.register(MachineryListing, MachineryListingAdmin)

# Register the OperatorListing model
class OperatorListingAdmin(admin.ModelAdmin):
    list_display = ['name', 'bio', 'certification', 'hourly_rate', 'available_from', 'available_to', 'user']
    list_filter = ['available_from', 'available_to', 'user']
    search_fields = ['name', 'user__username']
    ordering = ['available_from']

admin.site.register(OperatorListing, OperatorListingAdmin)

# Register the Wishlist model
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count']
    search_fields = ['user__username']

admin.site.register(Wishlist, WishlistAdmin)

# Register the RentalTransaction model
class RentalTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'machinery', 'operator', 'rental_start_date', 'rental_end_date', 'total_amount']
    list_filter = ['rental_start_date', 'rental_end_date', 'user']
    search_fields = ['user__username']
    ordering = ['rental_start_date']

admin.site.register(RentalTransaction, RentalTransactionAdmin)

# Register the Review model
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'comment', 'content_type', 'object_id']
    list_filter = ['content_type', 'rating', 'user']
    search_fields = ['user__username', 'content_type__model']

admin.site.register(Review, ReviewAdmin)
