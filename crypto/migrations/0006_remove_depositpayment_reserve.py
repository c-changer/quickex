# Generated by Django 5.0.1 on 2024-01-25 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0005_alter_depositpayment_reserve'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='depositpayment',
            name='reserve',
        ),
    ]
