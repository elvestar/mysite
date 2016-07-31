# -*- coding: utf-8 -*-

from django.shortcuts import render


def index(request):
    return render(request, 'cms/index.html')


def blog_viewer(request):
    file_items = [
        {'uri': 'blog/test', 'title': '测试的哈哈哈', 'date': '2016-02-23', 'last_update_time': '3 min ago', 'size': '1 MB'},
        {'uri': 'blog/ohno', 'title': '嘿嘿汪汪汪', 'date': '2016-02-23', 'last_update_time': '3 min ago', 'size': '1 MB'},
    ]
    return render(request, 'cms/viewer.html', {
        'file_items': file_items
    })


def life_viewer(request):
    return render(request, 'cms/viewer.html')


def notes_viewer(request):
    return render(request, 'cms/viewer.html')
