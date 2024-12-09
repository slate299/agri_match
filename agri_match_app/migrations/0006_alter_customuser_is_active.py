# Generated by Django 4.2.16 on 2024-12-10 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agri_match_app', '0005_alter_wishlist_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
