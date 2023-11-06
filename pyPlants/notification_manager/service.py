from pyPlants.data_classes.action_plant import ActionPlant
from pyPlants.models import NotificationType, Notification, NotificationCenter


class NotificationManager:
    """
    This class handles the logic of sending notifications to the user.
    """
    def __init__(self, notification_center: NotificationCenter, plant_action: ActionPlant):
        self.notification_center = notification_center
        self.should_send_in_app_notification = self.notification_center.enable_in_app_notifications
        self.should_send_email_notification = self.notification_center.enable_email_notifications
        self.should_send_sms_notification = self.notification_center.enable_sms_notifications
        self.plant_action = plant_action

    def send_notifications(self):
        """
        This method sends the notifications to the user based on what notification types are enabled.
        """
        notifications = list()
        if not self.plant_action.is_empty():
            if self.should_send_in_app_notification:
                notifications.append(self.send_in_app_notification())
            if self.should_send_email_notification:
                notifications.append(self.send_email_notification())
            if self.should_send_sms_notification:
                notifications.append(self.send_sms_notification())
        return notifications
    
    def send_in_app_notification(self):
        message = self.build_in_app_notification_message()
        notification = Notification.objects.create(
            user=self.notification_center.user, message=message, notification_type=NotificationType.IN_APP
        )
        notification.mark_as_sent()
        return notification
    
    def send_email_notification(self):
        message = self.build_email_notification_message()
        notification = Notification.objects.create(
            user=self.notification_center.user, message=message, notification_type=NotificationType.EMAIL
        )
        # send email logic here - async task(?)
        return notification
    
    def send_sms_notification(self):
        message = self.build_sms_notification_message()
        notification = Notification.objects.create(
            user=self.notification_center.user, message=message, notification_type=NotificationType.SMS
        )
        # send sms logic here - async task(?)
        return notification

    def build_in_app_notification_message(self):
        message = f'Hey! It seems some of your plants need your attention! See below:'
        if self.plant_action.water:
            message += f'\nYou need to water: {", ".join(self.plant_action.water_plant_names())}.'
        if self.plant_action.fertilize:
            message += f'\nYou need to fertilize: {", ".join(self.plant_action.fertilize_plant_names())}.'
        if self.plant_action.repot:
            message += f'\nYou need to repot: {", ".join(self.plant_action.repot_plant_names())}.'
        return message
    
    def build_sms_notification_message(self):
        message = f'Hey! It seems some of your plants need your attention!'
        if self.plant_action.water:
            message += f'\n{self.plant_action.count_plants_to_repot()} plant(s) need to be watered.'
        if self.plant_action.fertilize:
            message += f'\n{self.plant_action.count_plants_to_fertilize()} plant(s) need to be fertilized.'
        if self.plant_action.repot:
            message += f'\n{self.plant_action.count_plants_to_repot()} plant(s) need to be repotted.'
        # note add a link to the app
        return message
    
    def build_email_notification_message(self):
        message = f'Hey! \n A friendly email to let you know that some of your plants need your attention! See below:'
        if self.plant_action.water:
            message += (f'\nYou need to water {self.plant_action.count_plants_to_water()} plant(s)!\n'
                        f'{", ".join(self.plant_action.water_plant_names())}.')
        if self.plant_action.fertilize:
            message += (f'\nYou need to fertilize {self.plant_action.count_plants_to_fertilize()} plant(s)!\n'
                        f'{", ".join(self.plant_action.fertilize_plant_names())}.')
        if self.plant_action.repot:
            message += (f'\nYou need to repot {self.plant_action.count_plants_to_repot()} plant(s)!\n'
                        f'{", ".join(self.plant_action.repot_plant_names())}.')
        # note add a link to the app
        return message
