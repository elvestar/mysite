from __future__ import unicode_literals

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
