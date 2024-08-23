from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()
# Create your views here.
def index(request):
    # context = {
    #     "user": request.user
    # }
    # return render(request, "pong/index.html", {"context": context})
    return render(request, "pong/test.html")
    
# def game_view(request, player1, player2):
#     player_1 = User.objects.get(username=player1)
#     player_2 = User.objects.get(username=player2)
#     if not player_1 or not player_2:
#         return Http404()
#     context = {
#         "user": request.user,
#         "player_1": player_1.username,
#         "player_2": player_2.username
#     }
#     return render(request, "pong/game.html", {"context": context})
