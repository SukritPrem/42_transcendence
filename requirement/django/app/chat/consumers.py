from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.shortcuts import get_object_or_404
# from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json
import sys
from django.core import serializers

class ChatroomConsumer(WebsocketConsumer):
	def connect(self):
		self.user = self.scope['user']
		self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
		self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
		async_to_sync(self.channel_layer.group_add)(
			self.chatroom_name, self.channel_name
		)


		# #add and update online users
		if self.user not in self.chatroom.users_online.all():
			self.chatroom.users_online.add(self.user)
			self.update_online_count()
		
		# sys.stderr.write(f"user: {self.user}\n")
		# sys.stderr.write(f"user online: {self.chatroom.users_online.count()}\n")

		self.accept()
		self.send(text_data=json.dumps({"online_count": "hello form server"}))

	def disconnect(self, close_code):
		# pass
		async_to_sync(self.channel_layer.group_discard)(
			self.chatroom_name, self.channel_name
		)

		# remove and update online users
		if self.user in self.chatroom.users_online.all():
			self.chatroom.users_online.remove(self.user)
			self.update_online_count()

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		type = text_data_json['type']
		event = {}
		if type == "message":	
			body = text_data_json['body']
			message = GroupMessage.objects.create(
				body = body,
				author = self.user,
				group = self.chatroom
			)
			event['message_id'] = message.id
			event['type'] = 'message_handler'
		
		if type == "invite_private_pong":
			event['type'] = 'invite_private_pong_handler'
			event['inviter'] = text_data_json['inviter']
			event['invited'] = text_data_json['invited']
			
		async_to_sync(self.channel_layer.group_send)(
			self.chatroom_name, event
		)

	def invite_private_pong_handler(self, event):
		self.send(text_data=json.dumps(event))	

	def message_handler(self, event):
		message_id = event['message_id']
		message = GroupMessage.objects.get(id=message_id)
		context = {
			'type': 'message_handler',
			'message': {
				'id': message.id,
				'body': message.body,
				'author': message.author.id,
			},
			'user': {
				'id': self.user.id,
				'username': self.user.username,
			},
		}
		self.send(text_data=json.dumps(context))

	def update_online_count(self):
		online_count = self.chatroom.users_online.count() - 1
		event = {
			'type': 'online_count_handler',
			'online_count': online_count
		}
		async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

	def online_count_handler(self, event):
		self.send(text_data=json.dumps(event))