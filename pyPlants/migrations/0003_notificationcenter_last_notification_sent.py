# Generated by Django 4.2.7 on 2023-11-02 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyPlants', '0002_alter_notificationcenter_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationcenter',
            name='last_notification_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
