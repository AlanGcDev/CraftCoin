# Generated by Django 5.1 on 2024-09-09 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CraftCoin', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_verified',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='verification_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
