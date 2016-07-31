from django.conf.urls import url

from . import views

app_name = 'cms'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^viewer/blog/$', views.blog_viewer, name='blog_viewer'),
    url(r'^viewer/notes/$', views.notes_viewer, name='notes_viewer'),
    url(r'^viewer/life/$', views.life_viewer, name='life_viewer'),
    ]
