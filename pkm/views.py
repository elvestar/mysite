# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from myssg.search import Searcher

# Create your views here.

def index(request):
    return render(request, 'pkm/index.html')


def search(request):
    searcher = Searcher()
    q = request.GET['q']
    search_results = searcher.search(q)
    results = list()
    for search_result in search_results:
        results.append({
            'text': search_result['text'],
            'title': search_result.get('title', ''),
            'path': search_result['path']
        })
    return HttpResponse(json.dumps(results))


def search(request):
    return render(request, 'pkm/search.html')


