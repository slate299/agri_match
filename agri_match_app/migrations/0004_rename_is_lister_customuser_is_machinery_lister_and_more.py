# Generated by Django 4.2.16 on 2024-12-08 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agri_match_app', '0003_alter_machinerylisting_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_lister',
            new_name='is_machinery_lister',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_wishlist_user',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_operator_lister',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_renter',
            field=models.BooleanField(default=True),
        ),
    ]
