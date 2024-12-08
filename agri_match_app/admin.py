from django.contrib import admin
from .models import CustomUser, MachineryCategory, MachineryType, MachineryListing, OperatorListing, Wishlist, RentalTransaction, Review

# Register Custom User model with admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter', 'is_active', 'date_joined']
    list_filter = ['is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['date_joined']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_admin', 'is_machinery_lister', 'is_operator_lister', 'is_renter')}),
    )

# Register all models in the admin interface
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)  # Optionally, if you want to prevent modifying Groups for CustomUser

admin.site.register(MachineryCategory)
admin.site.register(MachineryType)
admin.site.register(MachineryListing)
admin.site.register(OperatorListing)
admin.site.register(Wishlist)
admin.site.register(RentalTransaction)
admin.site.register(Review)
