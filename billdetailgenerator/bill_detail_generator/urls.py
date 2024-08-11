from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name="results"),
    path("download_csv/",views.download_as_csv,name='download_as_csv')
]