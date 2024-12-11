from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import MachineryListing, OperatorListing, CustomUser

# Create groups and permissions on migration
@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    try:
        # Create user groups
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
            "Renter": []
        }

        for group_name, permissions in groups.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            for codename, name in permissions:
                content_type = ContentType.objects.get_for_model(
                    MachineryListing if "machinery" in codename else OperatorListing
                )
                permission, _ = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name},
                )
                group.permissions.add(permission)

        print("User groups and permissions successfully created.")
    except Exception as e:
        print(f"Error during group creation: {e}")

# Assign user to group after signup
@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        try:
            group_name = None
            if instance.is_admin:
                group_name = "Admin"
            elif instance.is_machinery_lister:
                group_name = "Machinery Lister"
            elif instance.is_operator_lister:
                group_name = "Operator Lister"
            elif instance.is_renter:
                group_name = "Renter"

            if group_name:
                group = Group.objects.get(name=group_name)
                instance.groups.add(group)
                print(f"User '{instance.username}' added to group '{group_name}'.")
            else:
                print(f"No role assigned for user '{instance.username}'.")
        except Group.DoesNotExist:
            print(f"Group '{group_name}' does not exist.")
        except Exception as e:
            print(f"Error while assigning group: {e}")
