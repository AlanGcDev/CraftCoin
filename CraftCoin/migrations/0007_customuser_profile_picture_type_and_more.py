# Generated by Django 5.1 on 2024-09-10 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CraftCoin', '0006_customuser_password_reset_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_picture_type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.BinaryField(blank=True, editable=True, null=True),
        ),
    ]
