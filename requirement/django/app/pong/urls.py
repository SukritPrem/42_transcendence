from django.urls import path
from . import views

app_name = "pong"

urlpatterns = [
    path("", views.index, name="index"),
    # path("<player1>/<player2>/", views.game_view, name="game")
]