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
	players: list
	game_datas: list
	match_index: int
	channel_name: str
	# nicknames: str

	def __init__(self):
		super().__init__(type='tournament', action='update')
		self.players: Player = []
		self.game_datas: GameData = []
		self.match_index = -1
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

	def set_another_player_win(self, username: str):
		game_data: GameData = self.game_datas[self.match_index]
		another_player = game_data.player_one if game_data.player_one.name == username else game_data.player_two
		game_data.winner = another_player

	def is_player_in_match(self, username: str):
		game_data: GameData = self.game_datas[self.match_index]
		return game_data.player_one.name == username or game_data.player_two.name == username
	
	def player_update_direction(self, username, direction):
		game_data: GameData = self.game_datas[self.match_index]
		if game_data.player_one.name == username:
			game_data.player_one.set_move(direction)
		elif game_data.player_two.name == username:
			game_data.player_two.set_move(direction)

	def is_all_ready(self):
		for player in self.players:
			if player.status != 'ready':
				return False
		return True

	def shuffle_player(self):
		random.shuffle(self.players)

	def cleanup(self):
		self.action = 'update'
		self.players.clear()
		self.game_datas.clear()
		self.match_index = -1

		

		

