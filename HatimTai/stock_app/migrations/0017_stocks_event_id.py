# Generated by Django 3.2.9 on 2021-11-06 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0016_remove_event_event_id_custom'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocks',
            name='event_id',
            field=models.ForeignKey(db_column='event_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='stock_app.event'),
        ),
    ]
