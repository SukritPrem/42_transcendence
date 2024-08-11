from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import json
from .message import *
import sys
from channels.db import database_sync_to_async
import asyncio

User = get_user_model()

class PublicConsumer(AsyncWebsocketConsumer):

	available: str = [] # keep username
	private_rooms: PrivateMessageRoom = {} # keep PrivateMessageRoom
	channel_public: str = 'pong_public_message'
	tasks: asyncio.Task = {}

	async def connect(self):
		self.username: str = self.scope['user'].username
		self.available.append(self.username)
		await self.accept()
		await self.channel_layer.group_add(self.channel_public, self.channel_name)
		# await self.pong_private_message(self.available)

	async def disconnect(self, close_code):
		self.username = self.scope['user'].username
		if self.username not in self.available:
			await self.private_quit()
		await self.channel_layer.group_discard(self.channel_public, self.channel_name)
		if self.username in self.available:
			self.available.remove(self.username)

	async def receive(self, text_data):
		self.username = self.scope['user'].username
		data = json.loads(text_data)
		# print (data, file=sys.stderr)
		if data['type'] == 'private':
			await self.private(data)

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
			print (f"username: data['invited']['name'] join {room.channel_name}", file=sys.stderr)
			
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
		room: PrivateMessageRoom
		if data:
			room = self.private_rooms.get(data['channel_name'])
		else:
			for channel_name in self.private_rooms:
				if self.private_rooms[channel_name].inviter.name == username \
					or self.private_rooms[channel_name].invited.name == username:
					room = self.private_rooms[channel_name]
					break
				else:
					room = None
		if room:

			#debug
			print (f'username: {username} quit {room.channel_name}', file=sys.stderr)

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
					print (f'{room.channel_name} should save on this stage', file=sys.stderr)
					
					if not room.game_data.winner:
						room.game_data.winner = room.game_data.player_one.name \
							if room.game_data.player_one.name == username else room.game_data.player_two
					
					self.tasks[channel_name].cancel()

					print (f'the winner is {room.game_data.winner.name}', file=sys.stderr)
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


################## play pong ############################
	async def send_game_data(self, room: PrivateMessageRoom):

			# print (room, file=sys.stderr)

			try:
				# check game end or player disconnect
				while not room.game_data.end_game():
					room.game_data.init_game()
					await self.channel_layer.group_send(
						room.channel_name,
						{
							'type': self.channel_public,
							'data': room.to_dict()
						}
					)
					await asyncio.sleep(5)
					room.game_data.game_loop = True
					while room.game_data.game_loop:
						room.game_data.ball_move()
						room.game_data.player_move()
						await self.channel_layer.group_send(
							room.channel_name,
							{
								'type': self.channel_public,
								'data': room.to_dict()
							}
						)
						room.game_data.player_idle()
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

