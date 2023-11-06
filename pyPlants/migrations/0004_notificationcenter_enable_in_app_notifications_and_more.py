# Generated by Django 4.2.7 on 2023-11-06 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyPlants', '0003_alter_notification_sent_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationcenter',
            name='enable_in_app_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('EMAIL', 'EMAIL'), ('SMS', 'SMS'), ('IN_APP', 'IN_APP')], default='IN_APP', max_length=20),
        ),
        migrations.AlterField(
            model_name='notification',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]