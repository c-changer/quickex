# Generated by Django 5.0.1 on 2024-02-22 02:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0022_tgbot_alter_bank_reserve_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.RemoveField(
            model_name='exchange',
            name='email',
        ),
        migrations.RemoveField(
            model_name='exchange',
            name='fio',
        ),
    ]
