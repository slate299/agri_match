from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import MachineryListing, OperatorListing, CustomUser


# Create groups and permissions on migration
@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    try:
        # Define groups and their associated permissions
        groups = {
            "Admin": [],
            "Machinery Lister": [
                ("add_machinerylisting", "Can add machinery listing"),
                ("change_machinerylisting", "Can change machinery listing"),
                ("delete_machinerylisting", "Can delete machinery listing"),
            ],
            "Operator Lister": [
                ("add_operatorlisting", "Can add operator listing"),
                ("change_operatorlisting", "Can change operator listing"),
                ("delete_operatorlisting", "Can delete operator listing"),
            ],
            "Renter": [],
        }

        # Loop through each group and create it with the relevant permissions
        for group_name, permissions in groups.items():
            group, _ = Group.objects.get_or_create(name=group_name)

            # Add permissions for the group
            for codename, name in permissions:
                content_type = get_content_type(codename)
                permission, _ = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name},
                )
                group.permissions.add(permission)

        print("User groups and permissions successfully created.")

    except Exception as e:
        print(f"Error during group creation: {e}")


def get_content_type(codename):
    """
    Determines the content type based on the codename.
    """
    if "machinery" in codename:
        return ContentType.objects.get_for_model(MachineryListing)
    return ContentType.objects.get_for_model(OperatorListing)


@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        # New user logic (group assignment on creation)
        try:
            print(f"Assigning group for newly created user: {instance.username}")
            # Role to group mapping
            role_to_group = {
                "is_admin": "Admin",
                "is_machinery_lister": "Machinery Lister",
                "is_operator_lister": "Operator Lister",
                "is_renter": "Renter",
            }

            # Assign user to group based on their role
            for role, group_name in role_to_group.items():
                if getattr(instance, role, False):
                    try:
                        group = Group.objects.get(name=group_name)
                        instance.groups.add(group)
                        print(f"User '{instance.username}' added to group '{group_name}'.")
                    except Group.DoesNotExist:
                        print(f"Group '{group_name}' does not exist.")
        except Exception as e:
            print(f"Error during group assignment: {e}")

    else:
        # If it's an update (not a new user)
        try:
            print(f"Assigning group for existing user: {instance.username}")
            # Same group assignment logic for updated user
            role_to_group = {
                "is_admin": "Admin",
                "is_machinery_lister": "Machinery Lister",
                "is_operator_lister": "Operator Lister",
                "is_renter": "Renter",
            }

            for role, group_name in role_to_group.items():
                if getattr(instance, role, False):
                    try:
                        group = Group.objects.get(name=group_name)
                        instance.groups.add(group)
                        print(f"User '{instance.username}' added to group '{group_name}'.")
                    except Group.DoesNotExist:
                        print(f"Group '{group_name}' does not exist.")
        except Exception as e:
            print(f"Error during group assignment: {e}")
