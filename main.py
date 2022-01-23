import os
import pandas as pd
import numpy as np
import sys


class Player:
    def __init__(self, moves: list(), color: str(), representing_number: float()):
        self.moves = moves
        self.color = color
        self.representing_number = representing_number
        self.pawns = 12
        self.turns_played = 0

    def make_a_move(self):
        _turn = self.moves[self.turns_played]
        self.turns_played += 1
        return _turn


class BoardGame:
    def __init__(self, board_size: int, w_player: Player, b_player: Player):
        self.current_round = 0

        # The players are a Player object
        self.white_player = w_player
        self.black_player = b_player

        # board is a board_size by board_size pd.dataFrame
        self.board = self.initiate_a_board(board_size)
        self.board_size = board_size

        # The default first player is the white player
        self.who_is_playing = w_player

        # The score the a dictionary with the amount of paws each player took out
        self.score = {'white': 0, 'black': 0}

    def initiate_a_board(self, board_size):
        # This function takes the board size (int) and return a pd.dataFrame
        # Empty cells have 0.0 in them, illegal cells have Nan in them
        # Cells with pawns have the player's representing number in them
        data_dict = {0: [None, 2, None, 2, None, 2, None, 2],
                     1: [2, None, 2, None, 2, None, 2, None],
                     2: [None, 2, None, 2, None, 2, None, 2],
                     3: [0, None, 0, None, 0, None, 0, None],
                     4: [None, 0, None, 0, None, 0, None, 0],
                     5: [0.5, None, 0.5, None, 0.5, None, 0.5, None],
                     6: [None, 0.5, None, 0.5, None, 0.5, None, 0.5],
                     7: [0.5, None, 0.5, None, 0.5, None, 0.5, None]}
        _board = pd.DataFrame(data_dict).T

        return _board

    def switch_playing_player(self):
        # This function takes no input, it updates the current playing player
        if self.who_is_playing.color == 'white':
            self.who_is_playing = self.black_player
        else:
            self.who_is_playing = self.white_player

    def get_player_move(self):
        # This function takes no input and returns a requested move from the current player
        return self.who_is_playing.make_a_move()

    def is_the_pawn_there(self, current_location):
        # This function takes the current player's position
        # If the player does not have a pawn at the the current player's position, the game will stop
        now_playing = self.who_is_playing
        player_number = now_playing.representing_number

        if self.board[current_location[0]][current_location[1]] != player_number:
            print(f"\n\n### Illegal move, the {self.who_is_playing.color} player does not have a pawn "
                  f"at: {current_location} ###"
                  f"\n### The game will now end. ###\n\n")
            sys.exit(1)

    def check_destination(self, current, destination):
        # This function takes the position of the destination as a tuple and returns
        # what action the player should take, if the move is illegal, it stops the game.
        destination_current_content = self.board[destination[0]][destination[1]]
        possible_directions = self.possible_next_location(current)
        must_eat = self.should_eat(current)

        if destination not in possible_directions.values() and destination not in must_eat:
            print(f"You can't move there, illegal move at line {self.current_round}, "
                  f"the game will now end.")
            sys.exit(1)

        if destination_current_content == self.who_is_playing.representing_number:
            # A case which there is a player's own pawn already at the destination
            print(f"You can't move there, you already have a pawn there, illegal move at line {self.current_round}, "
                  f"the game will now end.")
            sys.exit(1)

        if len(must_eat) > 0 and destination not in must_eat:
            # A case which there the player is trying to aviod eating the opponent
            print(f"You can't move there, you must eat the opponent, illegal move at line {self.current_round},"
                  f"the game will now end.")
            sys.exit(1)

        if destination in must_eat:
            # A case which there is an opponent's pawn at the destination
            print("Nice move! take the opponent's pawn to hell!")
            return {'action': 'eat', 'destination': destination}

        else:
            return {'action': 'move', 'destination': destination}

    def possible_next_location(self, _current):
        # This function takes the current player's position
        # The function returns the possible locations to move to in
        if self.who_is_playing.color == 'white':
            move_factor = 1
        else:
            move_factor = -1

        next_row = _current[1] + move_factor
        right = _current[0] - move_factor
        left = _current[0] + move_factor

        if next_row >= self.board_size:
            forward = False
        else:
            forward = True

        if right < 0 or right > self.board_size - 1:
            right = 999

        if left < 0 or left > self.board_size - 1:
            left = 999

        right_option = (right, next_row)
        left_option = (left, next_row)

        return {'forward': forward, 'right': right_option, 'left': left_option}

    def should_eat(self, current):
        # This function takes the pawn's current position and returns the possible
        # eating locations
        eating_destinations = []
        possibility = self.possible_next_location(current)

        directions = ['left', 'right']
        possibilities = {}
        for direction in directions:
            if 999 not in possibility[direction]:
                possibilities[direction] = {'can_eat': False,
                                            'position': possibility[direction]}

        if len(possibilities) > 0:
            # A loop that checks if there is an opponent's pawn in the next 2
            # possible moving locations, if there is, it changes the "can_eat"
            # attribute to True
            for direction in possibilities:
                location = possibilities[direction]['position']
                if self.board[location[0]][location[1]] == (1 / self.who_is_playing.representing_number):
                    possibilities[direction]['can_eat'] = True

            for direction in possibilities:
                if possibilities[direction]['can_eat']:
                    next_possibilities = self.possible_next_location(possibilities[direction]['position'])
                    if next_possibilities['forward']:
                        _next = next_possibilities[direction]
                        if 999 not in _next and self.board[_next[0]][_next[1]] == 0.0:
                            eating_destinations.append(_next)

        return eating_destinations

    def run_a_game(self):
        number_of_w_player_moves = len(self.white_player.moves)
        number_of_b_player_moves = len(self.black_player.moves)

        number_of_game_moves = max(number_of_b_player_moves, number_of_w_player_moves)

        for __turn in range(number_of_game_moves):
            self.current_round = __turn + 1
            print(f"Round #{__turn + 1}\nScore: {self.score}\n")
            now_playing = self.who_is_playing

            the_move = self.get_player_move()

            _from = the_move['current']
            _to = the_move['move_to']

            print(f"It is the {now_playing.color}'s player turn to move.\n"
                  f"The player wants to move from {_from} to {_to}")

            # Check is the current position has a pawn in it.
            self.is_the_pawn_there(_from)

            # Check what's in the destination.
            what_to_do = self.check_destination(current=_from, destination=_to)

            if what_to_do['action'] == "move":
                self.move_a_pawn(current=_from, destination=_to)

            if what_to_do['action'] == "eat":
                self.eat_a_pawn(current=_from, destination=_to)
            if the_move['double_turn']:
                print("Double turn!!!")
            else:
                self.switch_playing_player()
            print(self.board)
            print('\n\n')

    def move_a_pawn(self, current, destination):
        # This function takes the current location of a pawn and it's destination.
        # The function updates the board accordingly
        self.board.at[current[1], current[0]] = 0.0
        self.board.at[destination[1], destination[0]] = self.who_is_playing.representing_number

    def eat_a_pawn(self, current, destination):
        # This function takes the current position and destination of the pawn and moves it
        # It updates the player's score, takes off an opponent's pawn and moves
        self.score[self.who_is_playing.color] += 1
        self.move_a_pawn(current, destination)
        opponent_location = (0.5 * (destination[0] + current[0]), 0.5 * (destination[1] + current[1]))
        self.board.at[opponent_location[1], opponent_location[0]] = 0.0


def list_of_moves(raw_moves):
    all_moves = []
    for raw_move in raw_moves:
        current = (int(raw_move[0]), int(raw_move[2]))
        move_to = (int(raw_move[4]), int(raw_move[6]))
        state = {'current': current, 'move_to': move_to}
        all_moves.append(state)

    return all_moves


turns_directory = r'E:\Documents\Python Scripts\Checkers'
file_name = input('Please enter file name: ')
turns = list(open(os.path.join(turns_directory, file_name + '.txt')))

white_turns = []
black_turns = []

turns = list_of_moves(turns)
counter = 0
doubles = False
last = False

turns_with_double_eating = []
while counter + 1 < len(turns):
    current_destination = turns[counter]['move_to']
    next_starting_point = turns[counter + 1]['current']

    if current_destination == next_starting_point:
        turns_with_double_eating.append([turns[counter], turns[counter + 1]])
        counter += 2
        doubles = True
        if counter == len(turns):
            last = True
    else:
        turns_with_double_eating.append(turns[counter])
        counter += 1

if doubles and not last:
    turns_with_double_eating.append(turns[counter])

for i, turn in enumerate(turns_with_double_eating):
    if i % 2 == 0:
        if isinstance(turn, list):
            for _turn in turn:
                _turn['double_turn'] = True
                white_turns.append(_turn)
            white_turns[-1]['double_turn'] = False
        else:
            turn['double_turn'] = False
            white_turns.append(turn)
    else:
        if isinstance(turn, list):
            for _turn in turn:
                _turn['double_turn'] = True
                black_turns.append(_turn)
            black_turns[-1]['double_turn'] = False
        else:
            turn['double_turn'] = False
            black_turns.append(turn)

white_player = Player(moves=white_turns, color='white', representing_number=2.0)
black_player = Player(moves=black_turns, color='black', representing_number=0.5)

board = BoardGame(board_size=8, w_player=white_player, b_player=black_player)

board.run_a_game()

black_final_score = board.score['black']
white_final_score = board.score['white']

if black_final_score == white_final_score:
    print('Incomplete game.')

else:
    winner_score = max(black_final_score, white_final_score)
    winner_name = list(board.score.keys())[list(board.score.values()).index(winner_score)]
    print(f'The winner is the {winner_name} player, with a score of: {winner_score}')

file_name = input("\n\nWasn't that nice? :-)")
