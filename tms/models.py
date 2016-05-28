from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ClockItem(models.Model):
    id = models.IntegerField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_hour = models.IntegerField()
    date = models.DateField(db_index=True)
    year = models.IntegerField()
    month = models.IntegerField()
    iso_year = models.IntegerField()
    week = models.IntegerField()
    weekday = models.IntegerField()

    thing = models.CharField(max_length=1024)
    time_cost_min = models.IntegerField()
    level = models.IntegerField(default=-1)
    category = models.CharField(max_length=1024)
    project = models.CharField(max_length=1024, )

    def __repr__(self):
        return '%s-%s-%s' % (self.start_time, self.end_time, self.thing)

    def __getitem__(self, item):
        return getattr(self, item)
