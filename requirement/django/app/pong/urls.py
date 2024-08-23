from django.urls import path
from . import views

app_name = "pong"

urlpatterns = [
    path("", views.index, name="index"),
    path("match_history/", views.match_history, name="match_history"),
    path("statictis/", views.statictis, name="statistic")
]