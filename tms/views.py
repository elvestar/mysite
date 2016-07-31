# -*- coding: utf-8 -*-

import json
from operator import itemgetter
from itertools import groupby
from datetime import datetime, date, timedelta

from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from rest_framework import generics, filters
from rest_framework.response import Response
import django_filters

from .serializers import ClockItemSerializer
from .models import ClockItem
from myssg.items import Item


CATEGORIES = ['工作', '学习', '生活', '其他']
CATEGORIES_NAME_DICT = {u'工作': 'work', u'学习': 'study', u'生活': 'life', u'其他': 'other'}
WEEK_DAY_STR = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


def time_cost_str(time_cost_min):
    if (time_cost_min % 60) < 10:
        minutes_str = '0' + str(time_cost_min % 60)
    else:
        minutes_str = str(time_cost_min % 60)
    return '%d:%s' % (time_cost_min / 60, minutes_str)


class ClockItemFilter(filters.FilterSet):
    min_st = django_filters.DateTimeFilter(name='start_time', lookup_type='gte')
    max_st = django_filters.DateTimeFilter(name='start_time', lookup_type='lt')

    class Meta:
        model = ClockItem
        fields = ['min_st', 'max_st', 'date', 'time_cost_min']


class ClockItemList(generics.ListAPIView):
    queryset = ClockItem.objects.all().order_by('start_time')
    serializer_class = ClockItemSerializer
    filter_fields = ['date']
    filter_class = ClockItemFilter


def index(request):
    return redirect('tms:day_report')


def project(request):
    return render(request, 'tms/project.html')


def calendar(request):
    return render(request, 'tms/calendar.html')


def report(request):
    dt = datetime.now()
    iso_year, week, weekday = dt.isocalendar()
    year = dt.year
    month = dt.month

    clock_items = ClockItem.objects.filter(iso_year=iso_year).all()
    return render(request, 'tms/report.html', {
        'clock_items': clock_items,
    })


def get_monday_date_of_iso_week(iso_year, week):
    ret = datetime.strptime('%04d-%02d-1' % (iso_year, week), '%Y-%W-%w')
    if date(iso_year, 1, 4).isoweekday() > 4:
        ret -= timedelta(days=7)
    return ret


def day_report(request):
    if 'date' in request.GET:
        return day_report_detail(request, request.GET['date'])

    days_num = 10
    cur_date = datetime.now().date()
    min_date = cur_date - timedelta(days=days_num - 1)
    days_stats_dict = dict()
    for i in range(days_num):
        dt = min_date + timedelta(days=i)
        days_stats_dict[dt] = {
            'date': dt,
            'date_str': dt.strftime('%Y-%m-%d'),
            'week_day': WEEK_DAY_STR[dt.weekday()],
            'all_time': 0,
            'valid_time': 0,
            'work_time': 0,
            'study_time': 0,
            'items_num': 0,
            'hours_stats': [{'work': 0, 'study': 0, 'life': 0, 'other': 0} for i in range(24)]
        }

    # Fill days_stats_dict
    clock_items = ClockItem.objects.filter(date__gte=min_date)
    for clock_item in clock_items:
        dt = clock_item.date
        time_cost_min = clock_item.time_cost_min
        days_stats_dict[dt]['all_time'] += time_cost_min
        days_stats_dict[dt]['items_num'] += 1
        category = clock_item.category
        if category == '工作':
            days_stats_dict[dt]['work_time'] += time_cost_min
            days_stats_dict[dt]['valid_time'] += time_cost_min
        elif category == '学习':
            days_stats_dict[dt]['study_time'] += time_cost_min
            days_stats_dict[dt]['valid_time'] += time_cost_min

        # Hour stats
        hours_stats = days_stats_dict[dt]['hours_stats']
        start_time = clock_item.start_time
        end_time = clock_item.end_time
        start_hour = start_time.hour
        end_hour = end_time.hour
        category_name = CATEGORIES_NAME_DICT[clock_item.category]
        if start_hour == end_hour:
            hours_stats[start_hour][category_name] += end_time.minute - start_time.minute
        else:
            for hour in range(start_hour, end_hour + 1):
                if hour == start_hour:
                    hours_stats[hour][category_name] += 60 - start_time.minute
                elif hour == end_hour:
                    hours_stats[hour][category_name] += end_time.minute
                else:
                    hours_stats[hour][category_name] += 60
    days_stats = list(days_stats_dict.values())
    days_stats.sort(key=itemgetter('date'), reverse=True)

    # Change time cost format
    for day_stats in days_stats:
        day_stats['work_time'] = time_cost_str(day_stats['work_time'])
        day_stats['study_time'] = time_cost_str(day_stats['study_time'])
        day_stats['valid_time'] = time_cost_str(day_stats['valid_time'])
        day_stats['all_time'] = time_cost_str(day_stats['all_time'])

    # Generate sparkline data, see http://omnipotent.net/jquery.sparkline/
    for day_stats in days_stats:
        sparkline_data = '['
        for hour_stats in day_stats['hours_stats']:
            sparkline_data += '[%d, %d, %d, %d], ' % (hour_stats['work'], hour_stats['study'], hour_stats['life'], hour_stats['other'])
        sparkline_data += ']'
        day_stats['sparkline_data'] = sparkline_data

    return render(request, 'tms/day_report.html', {
        'days_stats': days_stats
        })


def day_report_detail(request, date_str):
    cur_date_str = datetime.now().strftime('%Y-%m-%d')
    if date_str == cur_date_str:
        is_cur_day = True
    else:
        is_cur_day = False
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    prev_date_str = (dt - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date_str = (dt + timedelta(days=1)).strftime('%Y-%m-%d')

    clock_items = ClockItem.objects.filter(date=date_str).order_by('start_time')
    report_data = generate_report(clock_items, 1)
    return render(request, 'tms/day_report_detail.html', {
        'is_cur_day': is_cur_day,
        'date_str': date_str,
        'clock_items': clock_items,
        'prev_date_str': prev_date_str,
        'next_date_str': next_date_str,
        'report_data': report_data,
        })


def week_report(request):
    cur_iso_year, cur_week, weekday = datetime.now().isocalendar()
    if 'year' not in request.GET and 'week' not in request.GET:
        iso_year = cur_iso_year
        week = cur_week
    else:
        iso_year = int(request.GET['year'])
        week = int(request.GET['week'])

    if iso_year == cur_iso_year and week == cur_week:
        is_cur_week = True
    else:
        is_cur_week = False

    dt = get_monday_date_of_iso_week(iso_year, week)
    dt_of_prev_monday = dt - timedelta(days=7)
    dt_of_next_monday = dt + timedelta(days=7)
    iso_year_of_prev_week, prev_week, weekday = dt_of_prev_monday.isocalendar()
    iso_year_of_next_week, next_week, weekday = dt_of_next_monday.isocalendar()

    clock_items = ClockItem.objects.filter(iso_year=iso_year, week=week).order_by('start_time')

    report_data = generate_report(clock_items, 7)
    daily_overview = generate_daily_overview(clock_items)

    return render(request, 'tms/week_report.html', {
        'is_cur_week': is_cur_week,
        'iso_year': iso_year,
        'week': week,
        'clock_items': clock_items,
        'prev_week': prev_week,
        'iso_year_of_prev_week': iso_year_of_prev_week,
        'next_week': next_week,
        'iso_year_of_next_week': iso_year_of_next_week,
        'report_data': report_data,
        # 'daily_overview': daily_overview,
    })


def custom_report(request):
    start_time_str = request.GET['start']
    start_time = datetime.strptime(start_time_str, '%Y%m%d')
    start_time_str = start_time.strftime('%Y-%m-%d')
    end_time_str = request.GET['end']
    end_time = datetime.strptime(end_time_str, '%Y%m%d') + timedelta(days=1)
    end_time_str = end_time.strftime('%Y-%m-%d')

    clock_items = ClockItem.objects.filter(start_time__gte=start_time, end_time__lt=end_time).order_by('start_time')
    days_num = (end_time - start_time).days
    report_data = generate_report(clock_items, days_num)

    return render(request, 'tms/custom_report.html', {
        'start_time_str': start_time_str,
        'end_time_str': end_time_str,
        'days_num': days_num,
        'clock_items': clock_items,
        'report_data': report_data,
        })


def year_report(request):
    cur_year = datetime.now().year
    if 'year' not in request.GET:
        year = cur_year
    else:
        year = request.GET['year']

    return render(request, 'tms/year_report.html', {
        'year': year
    })


def week_stats(request):
    iso_year = int(request.GET['year'])
    week = int(request.GET['week'])
    week_data_group_by_category = ClockItem.objects.filter(iso_year=iso_year, week=week).\
        values('category').annotate(Count('id'), tc_sum=Sum('time_cost_min')).\
        order_by('-tc_sum')
    week_data_group_by_category = list((i['category'], i['id__count'], i['tc_sum'])
                                       for i in week_data_group_by_category)
    week_data_group_by_project = ClockItem.objects.filter(iso_year=iso_year, week=week). \
        values('project', 'category').annotate(Count('id'), tc_sum=Sum('time_cost_min')).\
        order_by('-tc_sum')

    week_data_group_by_project = list((i['category'], i['project'], i['id__count'], i['tc_sum'])
                                      for i in week_data_group_by_project)

    legend_data = list(t[0] for t in week_data_group_by_category)
    legend_data.sort(key=lambda x: CATEGORIES.index(x))
    week_data_group_by_category.sort(key=lambda x: CATEGORIES.index(x[0]))
    week_data_group_by_project.sort(key=lambda x: legend_data.index(x[0]))
    inner_data = list({'name': t[0], 'value': t[2]} for t in week_data_group_by_category)
    outer_data = list({'name': t[1], 'value': t[3]} for t in week_data_group_by_project)
    return JsonResponse({
        'legend': legend_data,
        'inner': inner_data,
        'outer': outer_data,
    })


def year_stats_step_by_month_and_week(request):
    """
    data = {
        'labels': ['一月', '二月', '三月', '...'],
        'valid_time': [15, 50, 33, ...],
        'work_time': [1.7, 25, 22, ...],
        'study_time': [13, 25, 11, ...],
    }
    """
    year = int(request.GET['year'])
    time_cost_group_by_month_category = ClockItem.objects.filter(year=year). \
        values('month', 'category').annotate(Sum('time_cost_min'), Count('time_cost_min'))

    valid_time_of_month = [0] * 12
    work_time_of_month = [0] * 12
    study_time_of_month = [0] * 12
    for item in time_cost_group_by_month_category:
        category = item['category']
        month = item['month']
        time_cost_min = item['time_cost_min__sum']
        if category == '工作':
            work_time_of_month[month - 1] += time_cost_min
            valid_time_of_month[month - 1] += time_cost_min
        elif category == '学习':
            study_time_of_month[month - 1] += time_cost_min
            valid_time_of_month[month - 1] += time_cost_min
    month_labels = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    valid_time_of_month = ['%.1f' % (float(i) / 60.0) for i in valid_time_of_month]
    work_time_of_month = ['%.1f' % (float(i) / 60.0) for i in work_time_of_month]
    study_time_of_month = ['%.1f' % (float(i) / 60.0) for i in study_time_of_month]

    # Get last week of year
    time_cost_group_by_week_category = ClockItem.objects.filter(iso_year=year). \
        values('week', 'category').annotate(Sum('time_cost_min'), Count('time_cost_min'))
    last_day_of_year = datetime(year=year, month=12, day=31)
    last_week = last_day_of_year.isocalendar()[1]

    valid_time_of_week = [0] * last_week
    work_time_of_week = [0] * last_week
    study_time_of_week = [0] * last_week
    for item in time_cost_group_by_week_category:
        category = item['category']
        week = item['week']
        time_cost_min = item['time_cost_min__sum']
        if category == '工作':
            work_time_of_week[week - 1] += time_cost_min
            valid_time_of_week[week - 1] += time_cost_min
        elif category == '学习':
            study_time_of_week[week - 1] += time_cost_min
            valid_time_of_week[week - 1] += time_cost_min
    week_labels = ['W%d' % w for w in range(1, last_week + 1)]
    valid_time_of_week = ['%.1f' % (float(i) / 60.0) for i in valid_time_of_week]
    work_time_of_week = ['%.1f' % (float(i) / 60.0) for i in work_time_of_week]
    study_time_of_week = ['%.1f' % (float(i) / 60.0) for i in study_time_of_week]

    data = {
        'month': {
            'labels': month_labels,
            'valid_time': valid_time_of_month,
            'work_time': work_time_of_month,
            'study_time': study_time_of_month,
            },
        'week': {
            'labels': week_labels,
            'valid_time': valid_time_of_week,
            'work_time': work_time_of_week,
            'study_time': study_time_of_week,
        }
    }

    return JsonResponse(data)


def generate_daily_overview(clock_items):
    pass


def generate_report(clock_items, days_num):
    """
    Sample data
        report_data = {
            'categories': [
                {
                    'name': '工作',
                    'projects': [
                        {
                            'name': 'XX项目',
                            'things': [
                                {
                                    'name': 'XXX模块开发',
                                    'time_cost': 30,
                                    },

                                ]
                        }
                    ]
                }
            ]
        }
    """
    categories_data = list()
    project_id = 1
    total_cost = 0
    for clock_item in clock_items:
        category = clock_item.category
        project = clock_item.project
        thing = clock_item.thing
        time_cost_min = clock_item.time_cost_min
        total_cost += time_cost_min

        # Find category
        category_data = None
        for it in categories_data:
            if it['name'] == category:
                category_data = it
                break
        if category_data is None:
            category_data = {
                'name': category,
                'cost': time_cost_min
            }
            categories_data.append(category_data)
        else:
            category_data['cost'] += time_cost_min

        if 'projects' not in category_data:
            category_data['projects'] = list()
        projects_data = category_data['projects']

        # Find project
        project_data = None
        for it in projects_data:
            if it['name'] == project:
                project_data = it
                break
        if project_data is None:
            project_data = {
                'name': project,
                'id': project_id,
                'cost': time_cost_min
            }
            project_id += 1
            projects_data.append(project_data)
        else:
            project_data['cost'] += time_cost_min

        if 'things' not in project_data:
            project_data['things'] = list()
        things_data = project_data['things']

        # Find thing
        thing_data = None
        for it in things_data:
            if it['name'] == thing:
                thing_data = it
                break
        if thing_data is None:
            thing_data = {
                'name': thing,
                'cost': time_cost_min
            }
            things_data.append(thing_data)
        else:
            thing_data['cost'] += time_cost_min

    # Calculate percentage
    minutes_of_days = days_num * 24 * 60
    for category_data in categories_data:
        category_data['pct'] = "{0:.1f}%".format(float(category_data['cost'])/minutes_of_days * 100)
        category_time_cost = category_data['cost']
        for project_data in category_data['projects']:
            project_data['pct'] = "{0:.1f}%".format(float(project_data['cost'])/category_time_cost * 100)

    # Sort
    categories_data.sort(key=lambda x: CATEGORIES.index(x['name']))
    for category_data in categories_data:
        projects_data = category_data['projects']
        projects_data.sort(key=itemgetter('cost'), reverse=True)
        for project_data in projects_data:
            thing_data = project_data['things']
            thing_data.sort(key=itemgetter('cost'), reverse=True)

    # Change form of time cost
    for category_data in categories_data:
        category_data['cost'] = time_cost_str(category_data['cost'])
        for project_data in category_data['projects']:
            project_data['cost'] = time_cost_str(project_data['cost'])

    report_data = {
        'categories': categories_data,
        'total_cost': total_cost
    }

    return report_data

