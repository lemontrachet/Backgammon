import numpy as np
from numpy.random import randint, choice
import itertools
from time import gmtime, mktime
import datetime

class Board():
    
    def __init__(self):
        board = np.zeros(26)
        board[1] = 2
        board[12] = 5
        board[17] = 3
        board[19] = 5
        board[6] = -5
        board[8] = -3
        board[13] = -5
        board[24] = -2
        self.board = board
        self.x = Player("x", self.board)
        self.y = Player("y", self.board)

    def update_board(self, new_state):
        if new_state != []: self.board = new_state
        self.draw_board()

    def draw_board(self):
        bottom_board = self.board[1:13]
        bottom_board = bottom_board[::-1]
        top_board = self.board[13:25]
        bb = ["|    |" if p == 0 else ("|x" + str(p) + "|" if p > 0 else
                     ("|y" + str(p * -1) + "|")) for p in bottom_board]
        tb = ["|    |" if p == 0 else ("|x" + str(p) + "|" if p > 0 else
                        ("|y" + str(p * -1) + "|")) for p in top_board]
        tbs, bbs = "", ""
        for p in bb:
            bbs += p
        for p in tb:
            tbs += p
        print()
        print(tbs)
        print()
        print(bbs)
        print()
        print("x bar:", self.board[0])
        print("y bar:", self.board[25])


class Player():
    
    def __init__(self, name, board):
        self.name = name
        self.board = board
    
    # two random numbers; four if the dice match
    def roll_dice():
        dice = (randint(1, 7), randint(1, 7))
        if dice[0] == dice[1]: dice = tuple(itertools.repeat(dice[0], 4))
        print(dice)
        return dice

    # generate all possible moves
    def gen_moves(board, die, player):
        new_states = []
        index = np.nonzero(board)
        
        # x's moves
        if player == "x": bar = board[0]
        else: bar = board[25]
        for space in index[0]:
            b2 = np.copy(board)
            # this player's pieces only
            if player == "x" and b2[space] > 0:
                move = space + die
                # pieces into end zone
                if move > 24:
                    b2[space] -= 1
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)
                # taking other player's piece
                elif b2[move] == -1:
                    b2[move] = 1
                    b2[space] -= 1
                    b2[25] -= 1 # putting a y piece on the bar
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)
                elif b2[move] >= 0:
                    b2[move] += 1
                    b2[space] -= 1
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)
            
            # y's moves
            elif player == "y" and b2[space] < 0:
                move = space - die
                # pieces in end zone
                if move <= 0:
                    b2[space] += 1
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
                # taking other player's piece
                elif b2[move] == 1:
                    b2[move] = -1
                    b2[space] += 1
                    b2[0] += 1 # x piece onto bar
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
                elif b2[move] <= 0:
                    b2[move] -= 1
                    b2[space] += 1
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
        return np.array(new_states)

    def calc_score(board, player):
        s = 0
        if player == "x":
            for space in board:
                if space > 0:
                    s += (space * board.index(space))
                    if space == 1: s -= 50
            return s
            
        else:
            for space in board:
                if space < 0:
                    s -= (space / board.index(space))
                    if space == -1: s += 50
            return s
                    
    # choose the best move by reference to resulting state of the board
    def evaluate_moves(board_states, player):
        if player == "x": factor = 1
        else: factor = -1
        best = [[], 0]
        for board in board_states:
            board = list(board)
            num_pieces = Player.get_num_pieces(board, player)
            s = Player.calc_score(board, player)
            if num_pieces == 0:
                best = [board, s]
                best[1] *= factor
                return best
            s += (15 - num_pieces) * 10 * factor # bonus for pieces at goal
            if (s * factor) > best[1]: best = [board, s]
        best[1] *= factor # returns a positive value for comparison
        return best


    def get_num_pieces(board, player):
        if player == "x": f = lambda x: x > 0
        else: f = lambda x: x < 0
        return sum([x for x in board if f(x)])
        
    def check_remaining(first_die_moves, player):
        for m in first_die_moves:
            if Player.get_num_pieces(m, player) == 0:
                return m
        return []
            

    def take_turn(self, board, player):
        print(player)
        dice = Player.roll_dice()
        first_die_moves = Player.gen_moves(board.board, dice[0], player)
        fm = Player.check_remaining(first_die_moves, player)
        if fm != []: return fm
        second_die_moves = []
        for m in first_die_moves:
            second_die_moves.append(Player.gen_moves(m, dice[1], player))
        best = ([], 0)
        for moves in second_die_moves:
            b = Player.evaluate_moves(moves, player)
            if b[1] > best[1]: best = b
        return best[0]
        

class Game_Manager():
    
    def __init__(self):
        self.board = Board()
        self.x = self.board.x
        self.y = self.board.y
    
    def play_game(self):
        turn = 1
        while True:
            #t = mktime(gmtime())
            #while mktime(gmtime()) < t + 0.1:
            #    pass
            if turn % 2 != 0:
                # x's move
                new_state = self.x.take_turn(self.board, "x")
                #print(new_state)
            else:
                # y's move
                new_state = self.y.take_turn(self.board, "y")
                #print(new_state)
            self.board.update_board(new_state)
            b = self.board.board
            
            if len([i for i in b if i > 0]) == 0:
                print("x wins")
                break
            elif len([i for i in b if i < 0]) == 0:
                print("y wins")
                break
            turn += 1
            
                

gm = Game_Manager()
gm.play_game()
