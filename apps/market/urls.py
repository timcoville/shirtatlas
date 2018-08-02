from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^editprofile$', views.editprofile),
    url(r'^editpassword$', views.editpassword),
    url(r'^newdesign$', views.newdesign),
    url(r'^test$', views.test),
    url(r'^(?P<id>\d+)$', views.design)
]
