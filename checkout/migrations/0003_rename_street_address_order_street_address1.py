# Generated by Django 4.2 on 2024-10-14 17:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_orderlineitem_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='street_address',
            new_name='street_address1',
        ),
    ]
