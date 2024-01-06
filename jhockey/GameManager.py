from enum import Enum, auto

class GameState(Enum):
    '''
    Enum to represent the state of the game.
    '''
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()

class GameManager:
    '''
    Class to manage score, time, and other game information.
    Arbitrates communication between the game controller and the teams.
    '''
    def __init__(self):
        self.score = {'red': 0, 'blue': 0}
        self.time = 0
        self.game_state: GameState = GameState.STOPPED
