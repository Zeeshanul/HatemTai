# Generated by Django 3.2.9 on 2021-11-06 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0010_event_event_custom_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_custom_id',
            new_name='event_id_custom',
        ),
    ]
