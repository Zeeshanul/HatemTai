# Generated by Django 3.2.9 on 2021-11-06 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0014_remove_event_eventid_custom'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_id_custom',
            field=models.CharField(blank=True, max_length=5000, unique=True),
        ),
    ]
