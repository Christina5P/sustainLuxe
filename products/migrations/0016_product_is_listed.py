# Generated by Django 4.2 on 2024-10-21 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_product_listed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_listed',
            field=models.BooleanField(default=False),
        ),
    ]
