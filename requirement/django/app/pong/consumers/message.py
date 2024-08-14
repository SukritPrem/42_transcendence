from dataclasses import dataclass, asdict
from .game_data import *
import random

@dataclass
class Message:
	type: str
	action: str

	def to_dict(self):
		return asdict(self)

@dataclass
class PrivateMessage(Message):
	def __init__(self, action: str):
		super().__init__(type='private', action=action)

@dataclass
class PrivateMessageError(PrivateMessage):
	message: str

	def __init__(self, message: str):
		super().__init__(action='error')
		self.message = message

@dataclass
class Player():
	name: str
	nickname: str
	status: str
	avatar: str = ''

	def __init__(self, name: str):
		self.name = name
		self.status = 'wait'
		self.nickname = None

@dataclass
class PrivateMessageRoom(PrivateMessage):
	inviter: Player
	invited: Player
	channel_name: str
	game_data: GameData

	def __init__(self, inviter: str, invited: str, ch=None):
		super().__init__(action='inviter')
		self.inviter = Player(name=inviter)
		self.invited = Player(name=invited)
		if not ch:
			ch = f'{self.type}_{self.inviter.name}_{self.invited.name}'
		self.channel_name = ch
		self.game_data = GameData()

	def get_player(self, username: str):
		if self.inviter.name == username:
			return self.inviter
		elif self.invited.name == username:
			return self.invited
		else:
			return None
	
	def get_another(self, player: Player):
		return self.invited if self.inviter is player else self.inviter

@dataclass
class TournamentMessage(Message):
	players: list # {nickname: Player()}
	game_datas: list
	match_index: int
	channel_name: str
	# nicknames: str

	def __init__(self):
		super().__init__(type='tournament', action='update')
		self.players: Player = []
		self.game_datas: GameData = []
		# self.nicknames: str = []
		self.match_index = 0
		self.channel_name = 'tournament_channel'

	def is_nickname_exist(self, nickname: str):
		for player in self.players:
			if player.nickname == nickname:
				return True
		return False

	def find_player(self, username: str):
		for player in self.players:
			if player.name == username:
				return player
		return None

	def is_all_ready(self):
		for player in self.players:
			if player.status != 'ready':
				return False
		return True

	def shuffle_player(self):
		random.shuffle(self.players)



		

