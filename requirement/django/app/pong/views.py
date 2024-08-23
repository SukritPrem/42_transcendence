from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.http import Http404
from .models import *
from django.db.models import Q
import sys

User = get_user_model()
# Create your views here.
def index(request):
    return render(request, "pong/test.html")
    
def match_history(request):
	user: User = request.user
	matches: list[Match] = Match.objects.filter(Q(player_one=user) | Q(player_two=user))[:5]
	# print (f'{matches}', file=sys.stderr)
	# data = serializers.serialize('json', matches)
	data = []
	for match in matches:
		# print (f'{match}', file=sys.stderr)
		outcome: str
		if match.winner is None:
			outcome = 'draw'
		else:
			outcome = 'win' if user.username == match.winner.username else 'lose'
		opponentPlayer: str
		if match.player_one is None or match.player_two is None:
			opponentPlayer = 'None'
		else:
			opponentPlayer = match.player_two.username if match.player_one.username == user.username else match.player_one.username
		
		data.append({
				'id': match.id,
				'matchType': match.match_type,
				'date': match.created,
				'opponentPlayer': opponentPlayer,
				'outcome': outcome
		})
	# return JsonResponse({'status': 'ok'}, safe=False,  status=200)
	return JsonResponse(data, safe=False,  status=200)

def statictis(request):
	user: User = request.user
	match_count = Match.objects.filter(Q(player_one=user) | Q(player_two=user)).count()
	match_win = Match.objects.filter(winner=user).count()
	match_draw = Match.objects.filter(Q(winner=None) & (Q(player_one=user) | Q(player_two=user))).count()
	match_lose = match_count - match_win - match_draw

	data = {
		'match': match_count,
		'win': match_win,
		'draw': match_draw,
		'lose': match_lose
	}
	return JsonResponse(data, safe=False,  status=200)