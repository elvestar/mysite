# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import re
from datetime import datetime, timedelta
from operator import itemgetter
from itertools import groupby

# TODO Use flask sqlalchemy temporarily
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from myssg.utils import ItemUtils


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tms:tms@localhost:3306/tms?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db = SQLAlchemy(app)


class ClockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    iso_year = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    weekday = db.Column(db.Integer, nullable=False)

    thing = db.Column(db.String(1024), nullable=False)
    time_cost = db.Column(db.Integer, nullable=False)  # In minute unites
    level = db.Column(db.Integer, nullable=False, default=-1)
    category = db.Column(db.String(1024), nullable=False)
    project = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return '%s-%s-%s' % (self.start_time, self.end_time, self.thing)

    def __getitem__(self, item):
        return getattr(self, item)

db.create_all()


class TimeAnalyzer(object):
    def __init__(self, settings):
        self.settings = settings

    def batch_analyze(self, html_roots):
        result = None
        for html_root in html_roots:
            result = self.analyze(html_root, append=True)
        return result

    def analyze(self, html_root, append=True):
        result = list()
        for table in html_root.find_all('table', class_='clock-table'):
            category, project, thing, level = self.get_thing_hierarchy(table)
            # print(category, project, thing, level)
            for tr in list(table.find_all('tr'))[1:]:
                start_clock_str = list(tr.children)[0].string
                end_clock_str = list(tr.children)[1].string
                start_time = datetime.strptime(start_clock_str[0:10] + ' ' + start_clock_str[-5:],
                                               '%Y-%m-%d %H:%M')
                if end_clock_str is None or end_clock_str == 'None':
                    end_time = start_time
                else:
                    end_time = datetime.strptime(end_clock_str[0:10] + ' ' + end_clock_str[-5:],
                                                 '%Y-%m-%d %H:%M')
                # We treat 5:00 am as beginning of a day
                if start_time.hour >= 5:
                    date = start_time.date()
                else:
                    date = start_time.date() - timedelta(days=1)
                iso_year, week, weekday = date.isocalendar()
                time_cost = (end_time - start_time).total_seconds() / 60
                clock_item = ClockItem(
                    start_time=start_time,
                    end_time=end_time,
                    start_hour=start_time.hour,
                    date=date,
                    year=date.year,
                    month=date.month,
                    iso_year=iso_year,
                    week=week,
                    weekday=weekday,

                    thing=thing,
                    level=level,
                    category=category,
                    project=project,
                    time_cost=time_cost)
                db.session.add(clock_item)
        db.session.commit()

        return result

    @staticmethod
    def get_thing_hierarchy(node):
        category = None
        project = None
        thing = None
        level = -1
        for sibling in node.previous_siblings:
            if level == -1:
                m = re.match(r'^h([1-6])', sibling.name)
                if m is not None:
                    level = int(m.group(1)) - 1
            if thing is None and sibling.name == 'h4':
                thing = sibling.string
            elif project is None and sibling.name == 'h3':
                project = sibling.string
            elif category is None and sibling.name == 'h2':
                category = sibling.string
                break
        if thing is None:
            if project is not None:
                thing = project
            else:
                thing = category
        return category, project, thing, level

    def dump_all(self):
        # self.dump_clock_items_by_date()
        self.dump_week_data()

    def dump_clock_items_by_date(self):
        start_date = datetime(year=2015, month=4, day=1).date()
        end_date = datetime.now().date()
        cur_date = start_date
        clock_items = ClockItem.query.order_by(ClockItem.start_time).all()
        print(len(clock_items))
        for ci_year, cis_of_year in groupby(clock_items, itemgetter('year')):
            cis_of_year_dict = dict()
            for ci_date, cis_of_date in groupby(clock_items, itemgetter('date')):
                cis = list()
                for ci in cis_of_date:
                    cis.append((ItemUtils.to_datetime(ci.start_time),
                                ItemUtils.to_datetime(ci.end_time),
                                ci.time_cost,
                                ci.category, ci.project, ci.thing))
                ci_date_str = ci_date.strftime('%Y-%m-%d')
                cis_of_year_dict[ci_date_str] = cis

            file_path = os.path.join(self.settings.OUTPUT_DIR, 'time/data/cis_%s.json' % ci_year)

            f = file(file_path, 'w')
            f.write(json.dumps(cis_of_year_dict))
            f.close()

    def dump_week_data(self):
        iso_year = 2016
        start_week = 1
        end_week = 21
        for week in range(start_week, end_week + 1):
            week_data_group_by_category = ClockItem.query. \
                with_entities(ClockItem.category,
                              db.func.count(), db.func.sum(ClockItem.time_cost)). \
                filter_by(iso_year=iso_year, week=week). \
                group_by(ClockItem.category).order_by(db.desc(db.func.sum(ClockItem.time_cost))).all()
            week_data_group_by_project = ClockItem.query. \
                with_entities(ClockItem.category, ClockItem.project,
                              db.func.count(), db.func.sum(ClockItem.time_cost)). \
                filter_by(iso_year=iso_year, week=week). \
                group_by(ClockItem.project).order_by(db.desc(db.func.sum(ClockItem.time_cost))).all()

            categories = ['工作', '学习', '生活', '其他']
            legend_data = list(t[0] for t in week_data_group_by_category)
            legend_data.sort(key=lambda x: categories.index(x))
            week_data_group_by_category.sort(key=lambda x: categories.index(x[0]))
            week_data_group_by_project.sort(key=lambda x: legend_data.index(x[0]))
            inner_data = list({'name': t[0], 'value': t[2]} for t in week_data_group_by_category)
            outer_data = list({'name': t[1], 'value': t[3]} for t in week_data_group_by_project)
            option = {
                'tooltip': {
                    'trigger': 'item',
                    'formatter': "{a} <br/>{b}: {c} min ({d}%)"
                },
                'legend': {
                    'orient': 'vertical',
                    'x': 'left',
                    'data': legend_data
                },
                'series': [
                    {
                        'name': '类别耗时',
                        'type': 'pie',
                        'radius': [0, '30%'],

                        'label': {
                            'normal': {
                                'position': 'inner'
                            }
                        },
                        'labelLine': {
                            'normal': {
                                'show': False
                            }
                        },
                        'data': inner_data
                    },
                    {
                        'name': '项目耗时',
                        'type': 'pie',
                        'selectedMode': 'single',
                        'radius': ['35%', '55%'],

                        'data':outer_data
                    }
                ]
            }
            file_path = os.path.join(self.settings.OUTPUT_DIR,
                                     'time/data/%dW%d.json' % (iso_year, week))
            f = file(file_path, 'w')
            f.write(json.dumps(option))
            f.close()

