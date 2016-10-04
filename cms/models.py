from __future__ import unicode_literals

from datetime import datetime

from django.db import models


# Create your models here.
class FileItem(models.Model):
    id = models.AutoField(primary_key=True)
    uri = models.CharField(max_length=1024)
    mtime = models.DateTimeField()
    date = models.DateTimeField()
    title = models.CharField(max_length=1024)
    content = models.TextField()
    output = models.TextField()
    file_size = models.IntegerField()

    def __repr__(self):
        return '%s-%s-%s' % (self.uri, self.date, self.mtime)


class Photo(models.Model):
    uri = models.CharField(max_length=255, unique=True)
    taken_time = models.DateTimeField(default=datetime.fromtimestamp(0))
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    has_gps_info = models.BooleanField(default=False)
    longitude = models.FloatField()
    latitude = models.FloatField()
    longitude_bd09 = models.FloatField()
    latitude_bd09 = models.FloatField()
    address = models.CharField(max_length=1024)
    country_code = models.IntegerField()
    city = models.CharField(max_length=255)

    camera = models.CharField(max_length=512)
    lens = models.CharField(max_length=512)
    focal_length = models.FloatField(default=-1)
    f_number = models.FloatField(default=-1)
    exposure_time = models.FloatField(default=-1)
    exposure_time_str = models.CharField(max_length=512)
    iso = models.IntegerField(default=-1)


