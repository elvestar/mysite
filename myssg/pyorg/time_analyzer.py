# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import datetime, timedelta

# TODO Use flask sqlalchemy temporarily
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tms:tms@localhost:3306/tms?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db = SQLAlchemy(app)


class ClockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    start_hour = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
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

db.create_all()


class TimeAnalyzer(object):
    def __init__(self):
        pass

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

    def query_clock_items_by_date(self, date):
        clock_items = ClockItem.query.filter(db.func.date(ClockItem.date) == date).order_by(ClockItem.start_time).all()
        print(clock_items)
        return clock_items

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


