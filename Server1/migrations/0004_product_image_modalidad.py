# Generated by Django 5.1 on 2024-09-13 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Server1', '0003_serverinfo_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_modalidad',
            field=models.ImageField(default=1, upload_to='products/modalidad'),
            preserve_default=False,
        ),
    ]
