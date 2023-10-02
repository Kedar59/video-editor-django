from django.urls import path
from . import views

urlpatterns=[
    path("",views.home,name="home"),
    path("trim/",views.trim,name="trim"),
    path("split/",views.split,name="split"),
    path("merge/",views.merge,name="merge"),
]