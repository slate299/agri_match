from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import MachineryListing, OperatorListing  # Import your models here


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

    # Permissions for Machinery Lister
    machinery_listing_content_type = ContentType.objects.get_for_model(MachineryListing)
    permission_add = Permission.objects.get(codename='add_machinerylisting',
                                            content_type=machinery_listing_content_type)
    permission_change = Permission.objects.get(codename='change_machinerylisting',
                                               content_type=machinery_listing_content_type)
    permission_delete = Permission.objects.get(codename='delete_machinerylisting',
                                               content_type=machinery_listing_content_type)
    machinery_lister_group.permissions.add(permission_add, permission_change, permission_delete)

    # Permissions for Operator Lister
    operator_listing_content_type = ContentType.objects.get_for_model(OperatorListing)
    permission_add_operator = Permission.objects.get(codename='add_operatorlisting',
                                                     content_type=operator_listing_content_type)
    permission_change_operator = Permission.objects.get(codename='change_operatorlisting',
                                                        content_type=operator_listing_content_type)
    permission_delete_operator = Permission.objects.get(codename='delete_operatorlisting',
                                                        content_type=operator_listing_content_type)
    operator_lister_group.permissions.add(permission_add_operator, permission_change_operator,
                                          permission_delete_operator)
