# Generated by Django 4.2 on 2024-11-14 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_alter_product_listed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='listed_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
