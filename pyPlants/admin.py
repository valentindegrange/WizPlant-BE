from django.contrib import admin

from pyPlants.models import PlantUser, Plant, NotificationCenter, Notification


class PlantUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_superuser')
    search_fields = ['email']
    list_filter = ['is_staff', 'is_superuser']


class NotificationCenterAdmin(admin.ModelAdmin):
    list_display = ('user', 'enable_email_notifications',
                    'enable_sms_notifications', 'preferred_notification_hour',
                    'last_notification_sent')
    search_fields = ['user']
    list_filter = ['enable_email_notifications', 'enable_sms_notifications',
                   'preferred_notification_hour']


class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'sun_exposure', 'water_frequency_summer',
                    'water_frequency_winter', 'last_watered', 'leaf_mist',
                    'fertilizer', 'fertilizer_season', 'last_fertilized',
                    'repotting', 'repotting_season', 'last_repotted')
    search_fields = ['name', 'user']
    list_filter = ['last_watered', 'last_fertilized', 'last_repotted']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'message', 'notification_type', 'sent', 'viewed', 'sent_at', 'viewed_at')
    search_fields = ['user', 'message']
    list_filter = ['sent', 'viewed']


admin.site.register(PlantUser, PlantUserAdmin)
admin.site.register(Plant, PlantAdmin)
admin.site.register(NotificationCenter, NotificationCenterAdmin)
admin.site.register(Notification, NotificationAdmin)
