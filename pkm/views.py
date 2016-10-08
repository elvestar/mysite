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
    if 'q' in request.GET:
        q = request.GET['q']
        results = searcher.search(q)
    else:
        results = None
    return render(request, 'pkm/search.html', {
        'q': q,
        'results': results,
    })




