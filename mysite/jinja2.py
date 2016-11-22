from __future__ import absolute_import  # Python 2 only

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse

from jinja2 import Environment
from myssg.utils import ItemUtils


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'to_weekday_ch': ItemUtils.to_weekday_ch,
        'timedelta_min': ItemUtils.timedelta_min,
        'time_cost_sum': ItemUtils.time_cost_sum,
    })
    return env