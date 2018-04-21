# -*- coding: utf-8 -*-

import json
from operator import itemgetter
from itertools import groupby
from datetime import datetime, date, timedelta

from jinja2 import Environment

from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import models
from django.db.models import Sum, Count
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
import django_filters

from .serializers import ClockItemSerializer
from .models import ClockItem
from tms.utils import Utils
from myssg.items import Item


CATEGORIES = ['工作', '学习', '生活', '其他']
CATEGORIES_NAME_DICT = {u'工作': 'work', u'学习': 'study', u'生活': 'life', u'其他': 'other'}
WEEK_DAY_STR = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class ClockItemFilter(filters.FilterSet):
    min_st = django_filters.DateTimeFilter(name='start_time', lookup_expr='gte')
    max_st = django_filters.DateTimeFilter(name='start_time', lookup_expr='lt')

    class Meta:
        model = ClockItem
        fields = ['min_st', 'max_st', 'date', 'category', 'project', 'thing']


class ClockItemList(generics.ListAPIView):
    queryset = ClockItem.objects.all().order_by('start_time')
    serializer_class = ClockItemSerializer
    filter_class = ClockItemFilter


def index(request):
    tms_begin_date = TMS_BEGIN_DATE
    tms_end_date = datetime.now().date()

    # week_data_group_by_category = ClockItem.objects.filter(iso_year=iso_year, week=week). \
    #     values('category').annotate(Count('id'), tc_sum=Sum('time_cost_min')). \
    #     order_by('-tc_sum')

    years_stats_dict = dict()
    tms_data_group_by_year_category = ClockItem.objects.values('year', 'category').\
        annotate(Count('time_cost_min'), tc_sum=Sum('time_cost_min'))
    for item in tms_data_group_by_year_category:
        year = item['year']
        category = item['category']
        tc_sum = item['tc_sum']
        if year not in years_stats_dict:
            years_stats_dict[year] = {
                'year': year,
                'work_time': 0,
                'study_time': 0,
                'all_time': 0,
                'valid_time': 0,
            }
        year_stats = years_stats_dict[year]
        if category == '工作':
            year_stats['work_time'] += tc_sum
            year_stats['valid_time'] += tc_sum
        elif category == '学习':
            year_stats['study_time'] += tc_sum
            year_stats['valid_time'] += tc_sum
        year_stats['all_time'] += tc_sum
    years_stats = list(year_stats for (year, year_stats) in years_stats_dict.items())
    years_stats.sort(key=itemgetter('year'), reverse=True)
    for year_stats in years_stats:
        year = year_stats['year']

        # 计算本年总天数
        begin_date = datetime(year=year, month=1, day=1).date()
        end_date = datetime(year=year, month=12, day=31).date()
        if begin_date < tms_begin_date:
            begin_date = tms_begin_date
        if end_date > tms_end_date:
            end_date = tms_end_date
        days_num = (end_date - begin_date).days + 1
        year_stats['days_num'] = days_num
        year_stats['avg_valid_time'] = Utils.min_to_hour(year_stats['valid_time'] / days_num)
        year_stats['all_time'] = Utils.min_to_hour(year_stats['all_time'])
        year_stats['work_time'] = Utils.min_to_hour(year_stats['work_time'])
        year_stats['study_time'] = Utils.min_to_hour(year_stats['study_time'])
        year_stats['valid_time'] = Utils.min_to_hour(year_stats['valid_time'])

    cur_dt = datetime.now()
    return render(request, 'tms/index.html', {
        'years_stats': years_stats,
        'cur_dt': cur_dt,
        'cur_year': cur_dt.year,
        'cur_month': cur_dt.month

    })


@api_view(['GET'])
def api_day_stats(request):
    date_str = request.GET['date']
    if 'days_num' in request.GET:
        days_num = int(request.GET['days_num'])
    else:
        days_num = 1
    min_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    max_date = min_date + timedelta(days=days_num)
    clock_items = ClockItem.objects.filter(start_time__gte=min_date, end_time__lt=max_date).order_by('start_time')
    days_stats = generate_days_stats(clock_items, min_date, days_num)
    report = generate_report(clock_items, days_num)
    return Response({
        'days_stats': days_stats,
        'report': report,
        'clock_items': ClockItemSerializer(clock_items, many=True).data,
    })



DEFAULT_MIN_DT = datetime(year=1970, month=1, day=1)
DEFAULT_MAX_DT = datetime(year=9999, month=12, day=31)
TMS_BEGIN_DATE = date(year=2015, month=2, day=20)


@api_view(['GET'])
def api_project_stats(request):
    if 'min_dt' in request.GET:
        min_dt = Utils.parse_dt_str(request.GET['min_dt'])
    else:
        min_dt = DEFAULT_MIN_DT
    if 'max_dt' in request.GET:
        max_dt = Utils.parse_dt_str(request.GET['max_dt'])
    else:
        max_dt = DEFAULT_MAX_DT

    category = request.GET['c']
    project = request.GET['p']
    thing = request.GET.get('t', None)
    clock_items = ClockItem.objects.filter(start_time__gte=min_dt, end_time__lt=max_dt).order_by('-start_time')
    if category is not None:
        clock_items = clock_items.filter(category=category)
    if project is not None:
        clock_items = clock_items.filter(project=project)
    if thing is not None:
        clock_items = clock_items.filter(thing=thing)
    clock_items = clock_items.order_by('start_time')
    if min_dt == DEFAULT_MIN_DT:
        min_dt = clock_items[0].start_time
    if max_dt == DEFAULT_MAX_DT:
        last_clock_item = clock_items[len(clock_items) - 1]
        print(last_clock_item.end_time, last_clock_item.thing)
        max_dt = last_clock_item.end_time

    days_num = (max_dt.date() - min_dt.date()).days + 1
    print(min_dt, max_dt, days_num)
    # if days_num > 500:
    if days_num > 200:
        # Months stats
        interval = 'month'
        stats = generate_months_stats(clock_items, min_dt.date(), max_dt.date())
    elif days_num > 100:
        # Weeks stats
        interval = 'week'
        stats = generate_weeks_stats(clock_items, min_dt.date(), max_dt.date())
    else:
        # Days stats
        interval = 'day'
        stats = generate_days_stats(clock_items, min_dt.date(), days_num, with_hours_stats=False)

    return Response({
        'min_dt': min_dt,
        'max_dt': max_dt,
        'category': category,
        'interval': interval,
        'stats': stats,
    })


def generate_months_stats(clock_items, min_date, max_date):
    first_first_date = date(year=min_date.year, month=min_date.month, day=1)
    days_stats_dict = dict()
    first_date = first_first_date
    while True:
        interval_id = Utils.get_month_id(first_date)
        days_stats_dict[interval_id] = {
            'id': interval_id,
            'date': first_date,
            'all_time': 0,
            'valid_time': 0,
            'work_time': 0,
            'study_time': 0,
            'items_num': 0,
            }
        one_day_next_month = first_date + timedelta(days=32)
        first_date = date(year=one_day_next_month.year, month=one_day_next_month.month, day=1)
        if first_date > max_date:
            break

    # Fill days_stats_dict
    for clock_item in clock_items:
        dt = clock_item.date
        interval_id = Utils.get_month_id(dt)
        time_cost_min = clock_item.time_cost_min
        days_stats_dict[interval_id]['all_time'] += time_cost_min
        days_stats_dict[interval_id]['items_num'] += 1
        category = clock_item.category
        if category == '工作':
            days_stats_dict[interval_id]['work_time'] += time_cost_min
            days_stats_dict[interval_id]['valid_time'] += time_cost_min
        elif category == '学习':
            days_stats_dict[interval_id]['study_time'] += time_cost_min
            days_stats_dict[interval_id]['valid_time'] += time_cost_min

    weeks_stats = list(days_stats_dict.values())
    weeks_stats.sort(key=itemgetter('date'))

    return weeks_stats


def generate_weeks_stats(clock_items, min_date, max_date):
    first_monday_date = min_date - timedelta(days=min_date.weekday())
    days_stats_dict = dict()
    monday_date = first_monday_date
    while True:
        week_id = Utils.get_week_id(monday_date)
        days_stats_dict[week_id] = {
            'id': week_id,
            'date': monday_date,
            'all_time': 0,
            'valid_time': 0,
            'work_time': 0,
            'study_time': 0,
            'items_num': 0,
            }
        monday_date += timedelta(days=7)
        if monday_date > max_date:
            break

    # Fill days_stats_dict
    for clock_item in clock_items:
        dt = clock_item.date
        week_id = Utils.get_week_id(dt)
        # print(dt)
        time_cost_min = clock_item.time_cost_min
        days_stats_dict[week_id]['all_time'] += time_cost_min
        days_stats_dict[week_id]['items_num'] += 1
        category = clock_item.category
        if category == '工作':
            days_stats_dict[week_id]['work_time'] += time_cost_min
            days_stats_dict[week_id]['valid_time'] += time_cost_min
        elif category == '学习':
            days_stats_dict[week_id]['study_time'] += time_cost_min
            days_stats_dict[week_id]['valid_time'] += time_cost_min

    weeks_stats = list(days_stats_dict.values())
    weeks_stats.sort(key=itemgetter('date'))

    return weeks_stats


def generate_days_stats(clock_items, min_date, days_num,
                        with_hours_stats=True, with_sparkline_data=False):
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
        }
        if with_hours_stats:
            days_stats_dict[dt]['hours_stats'] = [{'work': 0, 'study': 0, 'life': 0, 'other': 0} for i in range(24)]

    # Fill days_stats_dict
    for clock_item in clock_items:
        dt = clock_item.date
        # print(dt)
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

        if with_hours_stats:
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
                if end_hour < start_hour:
                    end_hour += 24
                for hour in range(start_hour, end_hour + 1):
                    if hour >= 24:
                        next_dt = dt + timedelta(days=1)
                        if next_dt not in days_stats_dict:
                            continue
                        hours_stats = days_stats_dict[next_dt]['hours_stats']
                        hour -= 24
                    if hour == start_hour:
                        hours_stats[hour][category_name] += 60 - start_time.minute
                    elif hour == end_hour or hour == end_hour - 24:
                        hours_stats[hour][category_name] += end_time.minute
                    else:
                        hours_stats[hour][category_name] += 60

    days_stats = list(days_stats_dict.values())
    days_stats.sort(key=itemgetter('date'), reverse=True)

    # 额外信息
    for day_stats in days_stats:
        day_stats['work_time_str'] = Utils.min_to_hour2(day_stats['work_time'])
        day_stats['study_time_str'] = Utils.min_to_hour2(day_stats['study_time'])
        day_stats['valid_time_str'] = Utils.min_to_hour2(day_stats['valid_time'])
        day_stats['all_time_str'] = Utils.min_to_hour2(day_stats['all_time'])

    # Sparkline data
    if with_sparkline_data:
        # Generate sparkline data, see http://omnipotent.net/jquery.sparkline/
        for day_stats in days_stats:
            sparkline_data = '['
            for hour_stats in day_stats['hours_stats']:
                sparkline_data += '[%d, %d, %d, %d], ' % (hour_stats['work'], hour_stats['study'], hour_stats['life'], hour_stats['other'])
            sparkline_data += ']'
            day_stats['sparkline_data'] = sparkline_data

    return days_stats


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
        category_data['cost'] = Utils.min_to_hour2(category_data['cost'])
        for project_data in category_data['projects']:
            project_data['cost'] = Utils.min_to_hour2(project_data['cost'])

    report_data = {
        'categories': categories_data,
        'total_cost': total_cost
    }

    return report_data



@api_view(['GET'])
def api_week_stats(request):
    iso_year = int(request.GET['year'])
    week = int(request.GET['week'])
    week_data_group_by_category = ClockItem.objects.filter(iso_year=iso_year, week=week). \
        values('category').annotate(Count('id'), tc_sum=Sum('time_cost_min')). \
        order_by('-tc_sum')
    week_data_group_by_category = list((i['category'], i['id__count'], i['tc_sum'])
                                       for i in week_data_group_by_category)
    week_data_group_by_project = ClockItem.objects.filter(iso_year=iso_year, week=week). \
        values('project', 'category').annotate(Count('id'), tc_sum=Sum('time_cost_min')). \
        order_by('-tc_sum')

    week_data_group_by_project = list((i['category'], i['project'], i['id__count'], i['tc_sum'])
                                      for i in week_data_group_by_project)

    legend_data = list(t[0] for t in week_data_group_by_category)
    legend_data.sort(key=lambda x: CATEGORIES.index(x))
    week_data_group_by_category.sort(key=lambda x: CATEGORIES.index(x[0]))
    week_data_group_by_project.sort(key=lambda x: legend_data.index(x[0]))
    inner_data = list({'name': t[0], 'value': t[2]} for t in week_data_group_by_category)
    outer_data = list({'name': t[1], 'value': t[3]} for t in week_data_group_by_project)
    return Response({
        'legend': legend_data,
        'inner': inner_data,
        'outer': outer_data,
        })


def get_project(request):
    category = request.GET['c']
    project = request.GET['p']
    clock_items = ClockItem.objects.filter(category=category, project=project).order_by('start_time')
    cis_num = len(clock_items)
    start_time = clock_items[0].start_time
    end_time = clock_items[cis_num - 1].end_time
    days_num = (end_time.date() - start_time.date()).days + 1
    return render(request, 'tms/project.html', {
        'category': category,
        'project': project,
        'clock_items': clock_items,
        'start_time': start_time,
        'end_time': end_time,
        'days_num': days_num
    })


def all_projects(request):
    year = None
    all_projects_stats = ClockItem.objects
    if year is not None:
        all_projects_stats = all_projects_stats.filter(year=year)
    all_projects_stats = all_projects_stats.values('category', 'project'). \
        annotate(tc_count=models.Count('id'), tc_sum=models.Sum('time_cost_min'),
                 start_time_min=models.Min('start_time'), end_time_max=models.Max('end_time')). \
        order_by('-tc_sum')
    for project_stats in all_projects_stats:
            project_stats['days_num'] = \
            (project_stats['end_time_max'].date() - project_stats['start_time_min'].date()).days + 1
    return render(request, 'tms/all_projects.html', {
        'all_projects_stats': all_projects_stats,
        })


def time_analyzer(request):
    category = request.GET['c']
    project = request.GET['p']
    clock_items = ClockItem.objects.filter(category=category, project=project).order_by('start_time')
    cis_num = len(clock_items)
    start_time = clock_items[0].start_time
    end_time = clock_items[cis_num - 1].end_time
    return render(request, 'tms/time_analyzer.html', {
        'category': category,
        'project': project,
        'clock_items': clock_items,
        'start_time': start_time,
        'end_time': end_time,
    })


def calendar(request):
    return render(request, 'tms/calendar.html')


def get_report(request):
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

    if 'num' in request.GET:
        days_num = int(request.GET['num'])
    else:
        days_num = 31
    cur_date = datetime.now().date()
    min_date = cur_date - timedelta(days=days_num - 1)
    clock_items = ClockItem.objects.filter(date__gte=min_date)
    days_stats = generate_days_stats(clock_items, min_date, days_num, with_sparkline_data=True)

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
        'date': dt,
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

    dt_of_this_monday = get_monday_date_of_iso_week(iso_year, week)
    dt_of_prev_monday = dt_of_this_monday - timedelta(days=7)
    dt_of_next_monday = dt_of_this_monday + timedelta(days=7)
    iso_year_of_prev_week, prev_week, weekday = dt_of_prev_monday.isocalendar()
    iso_year_of_next_week, next_week, weekday = dt_of_next_monday.isocalendar()

    clock_items = ClockItem.objects.filter(iso_year=iso_year, week=week).order_by('start_time')
    clock_items_list = list()
    for dt, clock_items_of_day in groupby(clock_items, itemgetter('date')):
        clock_items_list.append({
            'date': dt,
            'clock_items': list(clock_items_of_day),
        })


    print('This monday: ', dt_of_this_monday)
    report_data = generate_report(clock_items, 7)
    days_stats = generate_days_stats(clock_items, min_date=dt_of_this_monday.date(),
                                     days_num=7, with_sparkline_data=True)
    days_stats.sort(key=itemgetter('date'))

    return render(request, 'tms/week_report.html', {
        'is_cur_week': is_cur_week,
        'iso_year': iso_year,
        'week': week,
        'clock_items': clock_items,
        'clock_items_list': clock_items_list,
        'prev_week': prev_week,
        'iso_year_of_prev_week': iso_year_of_prev_week,
        'next_week': next_week,
        'iso_year_of_next_week': iso_year_of_next_week,
        'report_data': report_data,
        'days_stats': days_stats,
        # 'daily_overview': daily_overview,
    })


def custom_report(request):
    # 默认取上周五中午到本周五中午作为start_time和end_time
    today = datetime.now().date()
    # 获取本周四14点的datetime
    end_dt_of_work_week = datetime(year=today.year, month=today.month, day=today.day,
                                   hour=14, minute=0, second=0)
    end_dt_of_work_week += timedelta(3 - today.weekday())
    # 获取上周四14点的datetime
    begin_dt_of_work_week = end_dt_of_work_week - timedelta(weeks=1)

    start_time_str = request.GET.get('start', None)
    if start_time_str is None:
        start_time = begin_dt_of_work_week
    else:
        start_time = datetime.strptime(start_time_str, '%Y%m%d')
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M')

    end_time_str = request.GET.get('end', None)
    if end_time_str is None:
        end_time = end_dt_of_work_week
    else:
        end_time = datetime.strptime(end_time_str, '%Y%m%d') + timedelta(days=1)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M')

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
    tms_begin_date = TMS_BEGIN_DATE
    tms_end_date = datetime.now().date()
    cur_year = datetime.now().year
    if 'year' not in request.GET:
        year = cur_year
    else:
        year = int(request.GET['year'])
    clock_items = ClockItem.objects.filter(year=year).order_by('start_time')

    # 总体统计
    total_stats = dict()
    # 计算总天数
    begin_date = datetime(year=year, month=1, day=1).date()
    end_date = datetime(year=year, month=12, day=31).date()
    if begin_date < tms_begin_date:
        begin_date = tms_begin_date
    if end_date > tms_end_date:
        end_date = tms_end_date
    days_num = (end_date - begin_date).days + 1
    total_stats['days_num'] = days_num

    # 计算各项总时间
    all_time = 0
    work_time = 0
    study_time = 0
    valid_time = 0
    for clock_item in clock_items:
        time_cost_min = clock_item.time_cost_min
        category = clock_item.category
        all_time += time_cost_min
        if category in ['工作', '学习']:
            valid_time += time_cost_min
        if category in ['工作']:
            work_time += time_cost_min
        if category in ['学习']:
            study_time += time_cost_min
    total_stats['all_time'] = Utils.min_to_hour(all_time)
    total_stats['work_time'] = Utils.min_to_hour(work_time)
    total_stats['study_time'] = Utils.min_to_hour(study_time)
    total_stats['valid_time'] = Utils.min_to_hour(valid_time)
    total_stats['avg_valid_time'] = Utils.min_to_hour(valid_time / days_num)

    # 生成报表
    report_data = generate_report(clock_items, days_num)

    return render(request, 'tms/year_report.html', {
        'year': year,
        'begin_date': begin_date,
        'end_date': end_date,
        'clock_items': clock_items,
        'report_data': report_data,
        'total_stats': total_stats,
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
    while True:
        last_week = last_day_of_year.isocalendar()[1]
        if last_week != 1:
            break
        else:
            last_day_of_year -= timedelta(days=1)

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



