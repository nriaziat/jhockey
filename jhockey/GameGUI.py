from typing_extensions import Protocol
from jhockey.GameManager import GameState

class GameManager(Protocol):

    def update_state(self, state: GameState):
        '''
        Updates the game state.
        '''
        ...

    def update_score(self, team: str, score: int):
        '''
        Updates the score for a team.
        '''
        ...

class GameGUI:
    '''
    Web GUI to control the game, add score, monitor time, and start/stop gameplay.
    Optionally, monitor video feed. 
    '''
    def __init__(self):
        pass

    def update(self):
        pass

    def start(self, game_manager: GameManager):
        '''
        Start the game.
        '''
        game_manager.update_state(GameState.RUNNING)

    def stop(self, game_manager: GameManager):
        '''
        Stop the game.
        '''
        game_manager.update_state(GameState.STOPPED)
    
    def pause(self, game_manager: GameManager):
        '''
        Pause the game.
        '''
        game_manager.update_state(GameState.PAUSED)
    
    def add_score(self, team: str, game_manager: GameManager):
        '''
        Add score to a team.
        '''
        game_manager.update_score(team, 1)
    
