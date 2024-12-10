from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import MachineryListing, OperatorListing, CustomUser

# Create groups and permissions on migration
@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    # Create user groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    machinery_lister_group, _ = Group.objects.get_or_create(name='Machinery Lister')
    operator_lister_group, _ = Group.objects.get_or_create(name='Operator Lister')
    renter_group, _ = Group.objects.get_or_create(name='Renter')

    # Create permissions for Machinery Lister group
    machinery_listing_content_type = ContentType.objects.get_for_model(MachineryListing)
    permissions = [
        ('add_machinerylisting', 'Can add machinery listing'),
        ('change_machinerylisting', 'Can change machinery listing'),
        ('delete_machinerylisting', 'Can delete machinery listing'),
    ]
    for codename, name in permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=machinery_listing_content_type,
            defaults={'name': name}
        )
        machinery_lister_group.permissions.add(permission)

    # Create permissions for Operator Lister group
    operator_listing_content_type = ContentType.objects.get_for_model(OperatorListing)
    operator_permissions = [
        ('add_operatorlisting', 'Can add operator listing'),
        ('change_operatorlisting', 'Can change operator listing'),
        ('delete_operatorlisting', 'Can delete operator listing'),
    ]
    for codename, name in operator_permissions:
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=operator_listing_content_type,
            defaults={'name': name}
        )
        operator_lister_group.permissions.add(permission)


# Assign user to group after signup
@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_admin:
            instance.groups.add(Group.objects.get(name="Admin"))
        elif instance.is_machinery_lister:
            instance.groups.add(Group.objects.get(name="Machinery Lister"))
        elif instance.is_operator_lister:
            instance.groups.add(Group.objects.get(name="Operator Lister"))
        elif instance.is_renter:
            instance.groups.add(Group.objects.get(name="Renter"))
