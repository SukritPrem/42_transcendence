from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import json
from .message import *
import sys
from channels.db import database_sync_to_async
import asyncio

User = get_user_model()

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class PublicConsumer(AsyncWebsocketConsumer):

	available: str = [] # keep username
	private_rooms: PrivateMessageRoom = {} # keep PrivateMessageRoom
	channel_public: str = 'pong_public_message'
	tasks: asyncio.Task = {}
	tournament: TournamentMessage = TournamentMessage()

	async def connect(self):
		self.username: str = self.scope['user'].username
		self.available.append(self.username)
		await self.accept()
		await self.channel_layer.group_add(self.channel_public, self.channel_name)
		await self.pong_private_message(self.tournament.to_dict())

	async def disconnect(self, close_code):
		self.username = self.scope['user'].username
		if self.username not in self.available:
			await self.private_quit()
			await self.tour_quit()
		await self.channel_layer.group_discard(self.channel_public, self.channel_name)
		if self.username in self.available:
			self.available.remove(self.username)

	async def receive(self, text_data):
		self.username = self.scope['user'].username
		data = json.loads(text_data)
		if data['type'] == 'private':
			await self.private(data)
		elif data['type'] == 'tournament':
			await self.tour(data)
		else:
			print (data, file=sys.stderr)

	async def pong_public_message(self, event: dict):
		await self.send(text_data=json.dumps(event))

	async def pong_private_message(self, event: dict):
		message = {
			"type": "pong_private_message",
			"data": event
		}
		await self.send(text_data=json.dumps(message))

################################ private ##############################
	async def private(self, data):
		# print(data['action'], file=sys.stderr)
		if data['action'] == 'inviter':
			await self.private_inviter(data)
		elif data['action'] == 'invited':
			await self.private_invited(data)
		elif data['action'] == 'update':
			await self.private_update(data)
		elif data['action'] == 'playpong':
			await self.private_playpong(data)
		elif data['action'] == 'sendkey':
			await self.private_sendkey(data)
		elif data['action'] == 'quit':
			await self.private_quit(data)

	async def private_inviter(self, data: dict):
		username: str = self.scope['user'].username
		invited = data['invited']
		if username not in self.available or invited not in self.available:
			await self.pong_private_message(PrivateMessageError("User unavailable").to_dict())
		else:
			self.available.remove(self.username)
			self.available.remove(invited)
			room: PrivateMessageRoom = PrivateMessageRoom(self.username, invited)
			await self.channel_layer.group_add(room.channel_name, self.channel_name)
			# self.private_rooms.append(room)
			self.private_rooms[room.channel_name] = room
			await self.channel_layer.group_send(
				self.channel_public,
				{
					'type': self.channel_public,
					'data': room.to_dict()
				}
			)

	async def private_invited(self, data: dict):
		room: PrivateMessageRoom = self.private_rooms[data['channel_name']]
		if room:

			#debug
			# print (f"username: data['invited']['name'] join {room.channel_name}", file=sys.stderr)
			
			#set avatar avatar
			inviter = await self.get_user(data['inviter']['name'])
			invited = await self.get_user(data['invited']['name'])
			room.inviter.avatar = inviter.avatar.url
			room.invited.avatar = invited.avatar.url
			room.action = 'update'
			await self.channel_layer.group_add(room.channel_name, self.channel_name)
			await self.channel_layer.group_send(room.channel_name, {'type': self.channel_public,'data': room.to_dict()})

	async def private_quit(self, data: dict=None):
		username: str = self.scope['user'].username
		room: PrivateMessageRoom = None
		if data:
			room = self.private_rooms.get(data['channel_name'])
		else:
			for channel_name in self.private_rooms:
				if self.private_rooms[channel_name].inviter.name == username \
					or self.private_rooms[channel_name].invited.name == username:
					room = self.private_rooms[channel_name]
					break
		if room:

			#debug
			# print (f'username: {username} quit {room.channel_name}', file=sys.stderr)

			room.action = 'quit'
			channel_name = room.channel_name
			player: Player = room.get_player(self.username)
			player.status = 'quit'
			another: Player = room.get_another(player)
			if another.status != 'quit':
				#tell anothor player for quit room and channel layer
				await self.channel_layer.group_send(
					channel_name,
					{'type': self.channel_public,'data': room.to_dict()})
			# this is last player in room
			else:
				del self.private_rooms[channel_name]
				
				# it sure the game was started, del game task and save match to database
				if channel_name in self.tasks:
					#debug
					# print (f'{room.channel_name} should save on this stage', file=sys.stderr)
					
					if not room.game_data.winner:
						room.game_data.winner = room.game_data.player_one.name \
							if room.game_data.player_one.name == username else room.game_data.player_two
					
					self.tasks[channel_name].cancel()

					# print (f'the winner is {room.game_data.winner.name}', file=sys.stderr)
					del self.tasks[channel_name]

			await self.channel_layer.group_discard(channel_name, self.channel_name)
			self.available.append(self.username)

	async def private_update(self, data: dict):
		room: PrivateMessageRoom = self.private_rooms[data['channel_name']]
		if room:
			room.inviter.status = data['inviter']['status']
			room.invited.status = data['invited']['status']
			if room.inviter.status == 'ready' and room.invited.status == 'ready':
				room.action = 'beginpong'
				room.game_data.player_one.name = room.inviter.name
				room.game_data.player_two.name = room.invited.name
			await self.channel_layer.group_send(room.channel_name, {'type': self.channel_public,'data': room.to_dict()})

	async def private_playpong(self, data: dict):
		room: PrivateMessageRoom = self.private_rooms.get(data['channel_name'])
		if room:
			room.action = 'playpong'
			if room.channel_name not in self.tasks:
				self.tasks[room.channel_name] = asyncio.create_task(self.send_game_data(room))

	async def private_sendkey(self, data: dict):
		# print(data, file=sys.stderr)
		username: str = self.scope['user'].username
		room: PrivateMessageRoom = self.private_rooms.get(data['channel_name'])
		if room:
			player = room.game_data.select_player(username)
			if player:
				player.set_move(data['direction'])
		pass

################## tournament ###########################
	async def tour(self, data):
		if data["action"] == 'join':
			await self.tour_join(data)
		elif data["action"] == 'quit':
			await self.tour_quit(data)
		elif data["action"] == 'update':
			await self.tour_update(data)
		elif data["action"] == 'playpong':
			await self.tour_playpong(data)
		elif data["action"] == 'sendkey':
			await self.tour_sendkey(data)
		elif data["action"] == 'finish':
			await self.tour_finish(data)
		else:
			print(data, file=sys.stderr)
	
	async def tour_join(self, data: dict):
		user: str = self.scope['user']
		if user.username not in self.available:
			await self.pong_private_message(PrivateMessageError("User unavailable").to_dict())
		elif self.tournament.is_nickname_exist(data["nickname"]):
			await self.pong_private_message(PrivateMessageError("Nickname exist").to_dict())
		elif len(self.tournament.players) >= 4:
			await self.pong_private_message(PrivateMessageError("Tournament is full").to_dict())
		else:
			self.available.remove(user.username)
			player = Player(user.username)
			player.nickname = data["nickname"]
			player.avatar = user.avatar.url
			self.tournament.players.append(player)


			# add user to channel layer
			await self.channel_layer.group_add(self.tournament.channel_name, self.channel_name)
			
			await self.channel_layer.group_send(
				self.channel_public,
				{
					'type': self.channel_public,
					'data': self.tournament.to_dict()
				}
			)
			#debug
			# print(self.tournament, file=sys.stderr)

	async def tour_update(self, data: dict):
		username: str = self.scope['user'].username

		pyr = None
		for p in data['players']:
			if p['name']== username:
				pyr = p
	
		player = self.tournament.find_player(username)
		if player:
			player.status = pyr['status']
			await self.channel_layer.group_send(self.tournament.channel_name, {
				'type': self.channel_public,
				'data': self.tournament.to_dict()
			})

			# it sure last player ready call tour_create_match only one time
			if self.tournament.is_all_ready():
				print(f"{GREEN}all player are ready, should start tournament{RESET}", file=sys.stderr)
				# self.tournament.shuffle_player()
				# print(self.tournament.players, file=sys.stderr)
				# self.tournament.action = 'waitmatch'
				await self.tour_create_match(data)

	async def wait_to_begin_pong(self, sec: int):
		await asyncio.sleep(sec)
		self.tournament.action = 'beginpong'
		await self.channel_layer.group_send(
			self.tournament.channel_name,
			{
				'type': self.channel_public,
				'data': self.tournament.to_dict()
			}
		)

	async def tour_create_match(self, data: dict):
		if self.tournament.match_index + 1 > 2:
			print (f'{GREEN}Tournament finished should save match to database{RESET}', file=sys.stderr)
			for player in self.tournament.players:
				if player.status != 'quit':
					self.available.append(player.name)
			self.tournament.cleanup()
			await self.channel_layer.group_send(
				self.channel_public,
				{
					'type': self.channel_public,
					'data': self.tournament.to_dict()
				}
			)
			return
		
		self.tournament.match_index += 1
		game_data = GameData()
		self.tournament.game_datas.append(game_data)
		if self.tournament.match_index < 2:
			index = self.tournament.match_index
			game_data.player_one.set_name(self.tournament.players[index].name)
			game_data.player_one.set_nickname(self.tournament.players[index].nickname)
			game_data.player_two.set_name(self.tournament.players[index + 2].name)
			game_data.player_two.set_nickname(self.tournament.players[index + 2].nickname)
		else:
			game_data.player_one.set_name(self.tournament.game_datas[0].winner.name)
			game_data.player_one.set_nickname(self.tournament.game_datas[0].winner.nickname)
			game_data.player_two.set_name(self.tournament.game_datas[1].winner.name)
			game_data.player_two.set_nickname(self.tournament.game_datas[1].winner.nickname)

		self.tournament.action = 'waitmatch'

		#for update pongPublic
		await self.channel_layer.group_send(
			self.channel_public,
			{
				'type': self.channel_public,
				'data': self.tournament.to_dict()
			}
		)

		# await self.wait_to_begin_pong(10)
		asyncio.create_task(self.wait_to_begin_pong(10))

	async def tour_playpong(self, data: dict):
		print(f'{GREEN} task pong should begin{RESET}', file=sys.stderr)
		#if found player quit in this stage do not create task then make winner of game
		if self.tournament.channel_name not in self.tasks:
			self.tasks[self.tournament.channel_name] = asyncio.create_task(self.send_game_data(self.tournament))
			print(f'{GREEN} task pong created{RESET}', file=sys.stderr)
			self.tournament.action = 'playpong'
			await self.channel_layer.group_send(
			self.tournament.channel_name,
			{
				'type': self.channel_public,
				'data': self.tournament.to_dict()
			}
		)

	async def tour_finish(self, data:dict):
		print (f'{GREEN} tournament finish should create new match', file=sys.stderr)
		if self.tournament.channel_name in self.tasks:
			print (f'{RED} tournament finish should create new match', file=sys.stderr)
			del self.tasks[self.tournament.channel_name]
			await self.tour_create_match(data)



	async def tour_sendkey(self, data: dict):
		# print(f'{RED}{data}{RESET}', file=sys.stderr)
		username: str = self.scope['user'].username
		self.tournament.player_update_direction(username, data['direction'])
		pass

	async def tour_quit(self, data: dict=None):
		print(f'{RED} tour_quit work{RESET}', file=sys.stderr)
		username: str = self.scope['user'].username
		player: Player = self.tournament.find_player(username)

		if player is not None:
			if self.tournament.action == 'update':
				self.tournament.players.remove(player)
			else:
				print(f'{RED}{username} quit unexpected{RESET}', file=sys.stderr)
				player.status = 'quit'

				# check player is next or now game
				if self.tournament.is_player_in_match(username):
					# it sure the game was started, del game task and save match to database
					if self.tournament.channel_name in self.tasks:
						# await self.tasks[self.tournament.channel_name].cancel()
						del self.tasks[self.tournament.channel_name]

					print (f'{GREEN}{self.tournament.channel_name} should save on this stage{RESET}', file=sys.stderr)
					self.tournament.set_another_player_win(username)
					game_data: GameData = self.tournament.game_datas[self.tournament.match_index]
					print (f'{GREEN}match [{game_data.player_one.name} : {game_data.player_two.name}] was end{RESET}', file=sys.stderr)
					print (f'{GREEN}the winner is {game_data.winner.name}{RESET}', file=sys.stderr)
					self.tournament.action == 'finish'
				else:
					print (f'{GREEN}{username} not in present match it will check when match create {RESET}', file=sys.stderr)
		self.available.append(username)
		await self.channel_layer.group_send(
			self.channel_public,
			{
				'type': self.channel_public,
				'data': self.tournament.to_dict()
			}
		)
		await self.channel_layer.group_discard(self.tournament.channel_name, self.channel_name)

################## play pong ############################
	async def send_game_data(self, room):

			# print (f'{GREEN}{room}', file=sys.stderr)
			game_data: GameData = None
			if room.type == 'private':
				game_data = room.game_data
			elif room.type == 'tournament':
				game_data = room.game_datas[room.match_index]
			try:
				# check game end or player disconnect
				while not game_data.end_game():
					game_data.init_game()
					await self.channel_layer.group_send(
						room.channel_name,
						{
							'type': self.channel_public,
							'data': room.to_dict()
						}
					)
					await asyncio.sleep(5)
					game_data.game_loop = True
					while game_data.game_loop:
						game_data.ball_move()
						game_data.player_move()
						await self.channel_layer.group_send(
							room.channel_name,
							{
								'type': self.channel_public,
								'data': room.to_dict()
							}
						)
						game_data.player_idle()
						await asyncio.sleep(1 / 12)  # 12 frames per second

				#game end send status for tell all client close socket
				room.action = 'finish'
				await self.channel_layer.group_send(
					room.channel_name,
					{
						'type': self.channel_public,
						#the data should be stat of game
						'data': room.to_dict()
					}
				)
			except asyncio.CancelledError:
				pass

# database
	@database_sync_to_async
	def get_user(self, username: str):
		return get_object_or_404(User, username=username)


# data structure
'''
	{
		'type': 'tournament',
		'action': 'sendkey',
		'players': 
			[
				{
					'name': 'pnamnil',
					'nickname': 'ton',
					'status': 'ready',
					'avatar': '/user-media/avatars/small_pnamnil.webp'
				},
				{
					'name': 'spipitku',
					'nickname': 'prem',
					'status': 'ready',
					'avatar': '/user-media/avatars/small_spipitku.webp'
				},
				{
					'name': 'kburalek',
					'nickname': 'gran',
					'status': 'ready',
					'avatar': '/user-media/avatars/small_kburalek.webp'
				},
				{
					'name': 'plertsir',
					'nickname': 'first',
					'status': 'ready',
					'avatar': '/user-media/avatars/small_plertsir.webp'
				}
			],
		'game_datas': 
			[
				{
					'table': 
						{
							'width': 200,
							'height': 100
						},
					'ball':
						{
							'table': 
								{
									'width': 200,
									'height': 100
								},
							'mx': 5,
							'my': 2, 
							'x': 145, 
							'y': 68
						},
					'player_one': 
						{
							'name': 'pnamnil',
							'nickname': 'ton',
							'x': 0,
							'y': 50,
							'move': 'idle',
							'score': 0
						},
					'player_two': 
						{
							'name': 'kburalek',
							'nickname': 'gran',
							'x': 200,
							'y': 50,
							'move': 'idle',
							'score': 0
						}, 
					'player_radius': 10,
					'ball_radius': 4,
					'player_speed': 2,
					'max_score': 3,
					'game_loop': True,
					'winner': None
				}
			],
		'match_index': 0,
		'channel_name': 'tournament_channel', 
		'direction': 'right'}

'''