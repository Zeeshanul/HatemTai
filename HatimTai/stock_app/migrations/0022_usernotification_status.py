# Generated by Django 3.2.9 on 2021-11-27 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0021_notification_usernotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='status',
            field=models.CharField(default='Unread', max_length=25),
        ),
    ]
