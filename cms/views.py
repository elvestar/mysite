# -*- coding: utf-8 -*-

from django.shortcuts import render

from .models import FileItem


def index(request):
    all_file_items = FileItem.objects.values('uri').all()
    item_count_stats = {'all': 0, 'blog': 0, 'notes': 0, 'life': 0, 'other': 0}
    for file_item in all_file_items:
        uri = file_item['uri']
        item_count_stats['all'] += 1
        if uri.startswith('blog/'):
            item_count_stats['blog'] += 1
        elif uri.startswith('notes/'):
            item_count_stats['notes'] += 1
        elif uri.startswith('life/'):
            item_count_stats['life'] += 1
        else:
            item_count_stats['other'] += 1
    return render(request, 'cms/index.html', {
        'all_file_items': all_file_items,
        'item_count_stats': item_count_stats
    })


def blog_viewer(request):
    category = 'blog'
    if 'uri' in request.GET:
        return detail_viewer(request, category)
    return list_viewer(request, category)


def life_viewer(request):
    category = 'life'
    if 'uri' in request.GET:
        return detail_viewer(request, category)
    return list_viewer(request, category)


def notes_viewer(request):
    category = 'notes'
    if 'uri' in request.GET:
        return detail_viewer(request, category)
    return list_viewer(request, category)


def list_viewer(request, category):
    file_items = FileItem.objects.values('uri', 'title', 'date', 'file_size', 'mtime').\
        filter(uri__startswith=category + '/')
    return render(request, 'cms/viewer.html', {
        'file_items': file_items,
        'category': category,
    })


def detail_viewer(request, category):
    uri = request.GET['uri']
    file_item = FileItem.objects.get(uri=uri)
    return render(request, 'cms/detail_viewer.html', {
        'file_item': file_item,
        'category': category,
    })

