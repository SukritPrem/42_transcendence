from dataclasses import dataclass, asdict
from .game_data import *

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
	status: str
	avatar: str = ''

	def __init__(self, name: str):
		self.name = name
		self.status = 'wait'

@dataclass
class PrivateMessageRoom(PrivateMessage):
	inviter: Player
	invited: Player
	channel_name: str
	game_data: GameData

	def __init__(self, inviter: str, invited: str):
		super().__init__(action='inviter')
		self.inviter = Player(name=inviter)
		self.invited = Player(name=invited)
		self.channel_name = f'{self.type}_{self.inviter.name}_{self.invited.name}'
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
