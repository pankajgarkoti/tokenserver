import datetime
from django.utils import timezone
from django.db import models

# Create your models here.


class APIUser(models.Model):
    uid = models.TextField(primary_key=True)
    last_successful_request = models.DateTimeField(default=datetime.datetime.min)
    banned = models.BooleanField(default=False)
    current_token = models.TextField(default='')

    def recent_request(self):
        if (datetime.datetime.now(tz=timezone.utc) > self.last_successful_request) and (datetime.datetime.now(tz=timezone.utc) - self.last_successful_request <= datetime.timedelta(hours=6)):
            return True
        else:
            return False

    def get_token(self):
        return self.current_token

    def __str__(self):
        return self.uid
