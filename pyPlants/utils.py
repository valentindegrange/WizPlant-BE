import datetime


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<year>/<month>/<filename>
    return f"user_{instance.user.id}/{datetime.datetime.now().year}/{datetime.datetime.now().strftime('%m')}/{filename}"


def plant_pics_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/plant_pictures/user_<id>/<year>/<month>/<filename>
    return f"plant_pictures/{user_directory_path(instance, filename)}"


def plant_logos_directory_path(instance, filename):
    return f"plant_logos/{datetime.datetime.now().year}/{datetime.datetime.now().strftime('%m')}/{filename}"

