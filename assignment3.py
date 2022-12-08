#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:46:14 2022

@author: nathanvaartjes
"""

import numpy as np
import copy
from collections import defaultdict


class TicTacToe:

    def __init__(self):
        # to not get confused, bind X with 1 and O with 2
        self.X = 1
        self.O = 2

        # 0 is empty, 1 is X, 2 is O
        self.gameboard = np.zeros((3, 3))
        self.gameboard[1, 1] = self.O

    def check_if_win(self, gameboard) -> (bool, bool):  # returns X_win, O_win
        # check rows
        for row in gameboard:
            if np.all(row == self.X):
                return True, False
            elif np.all(row == self.O):
                return False, True
        # check columns
        for column in gameboard.T:
            if np.all(column == self.X):
                return True, False
            elif np.all(column == self.O):
                return False, True
        # check diagonals:
        for diag in np.diag(gameboard), np.diag(np.fliplr(gameboard)):
            if np.all(diag == self.X):
                return True, False
            elif np.all(diag == self.O):
                return False, True

        return False, False

    def make_random_move_O(self):
        # get empty cells
        empty_cells = np.where(self.gameboard == 0)
        # choose 1 empty cell
        choice = np.random.randint(0, len(empty_cells[0]))
        # get coordinates of schosen cell and put O
        X, Y = empty_cells[0][choice],  empty_cells[1][choice]
        self.gameboard[X, Y] = self.O

    def player_move_X(self, budget):

        values = []
        empty_cells = np.where(self.gameboard == 0)
        gameboard_copy = copy.deepcopy(self.gameboard)
        # for every possible move of X
        for X, Y in zip(empty_cells[0], empty_cells[1]):
            # make hypothetical move
            gameboard_copy[X, Y] = self.X
            # get its Q value
            value = self.calculate_Q(gameboard_copy, budget)
            values.append(value)
            # reset move
            gameboard_copy[X, Y] = 0
        # get best move
        move = np.argmax(values)
        move_value = np.max(values)

        print(f'Board:\n {self.return_gameboard(gameboard_copy)}\nmove: {move}\nvalue: {move_value}\n')

        # make move
        moveX, moveY = empty_cells[0][move], empty_cells[1][move]

        # update board in-place
        self.gameboard[moveX, moveY] = self.X

    def calculate_Q(self, board, budget: int) -> float:
        """" returns Q-value of board as float """

        Q_values_dict = defaultdict(int)

        # update Q-values for n iterations
        # TODO: change to while loop, until convergence
        for i in range(budget):
            Q_values_dict = self.get_Q_values(board, Q_values_dict)

        return Q_values_dict[str(board)]

    def get_Q_values(self, gameboard_copy, Q_values_dict):

        ### make X and O move and get value recursively

        # get empty cells
        empty_cells = np.where(gameboard_copy == 0)

        # take random O move,
        choice = np.random.randint(0, len(empty_cells[0]))
        # get coordinates of chosen cell and put O
        gameboard_copy_level2 = copy.deepcopy(gameboard_copy)
        X, Y = empty_cells[0][choice], empty_cells[1][choice]
        gameboard_copy_level2[X, Y] = self.O

        X_win, Y_win = self.check_if_win(gameboard_copy_level2)
        if X_win:
            Q_values_dict[str(gameboard_copy_level2)] = 1
            return  Q_values_dict
        elif Y_win:
            Q_values_dict[str(gameboard_copy_level2)] = 0
            return Q_values_dict

        # check if draw
        if not np.any(gameboard_copy_level2 == 0):
            Q_values_dict[str(gameboard_copy_level2)] = 0
            return  Q_values_dict

        # then, make random X move
        empty_cells = np.where(gameboard_copy_level2 == 0)
        choice = np.random.randint(0, len(empty_cells[0]))
        # get coordinates of chosen cell and put O
        X, Y = empty_cells[0][choice], empty_cells[1][choice]
        gameboard_copy_level2[X, Y] = self.X

        # check if terminal state (cant be draw, O always ends)
        X_win, Y_win = self.check_if_win(gameboard_copy_level2)
        if X_win:
            Q_values_dict[str(gameboard_copy_level2)] = 1
            return Q_values_dict
        elif Y_win:
            Q_values_dict[str(gameboard_copy_level2)] = 0
            return Q_values_dict

        # if not terminal state, get Q value recursively
        Q_values_dict = self.get_Q_values(
            gameboard_copy_level2, Q_values_dict)

        # then, update scores via child Q-values
        # score is the max of the children
        # average over moves of O, maxify over moves of X:
        X_values = []
        for Xx, Yx in zip(empty_cells[0], empty_cells[1]):
            gameboard_copy[Xx, Yx] = self.X
            O_values = []
            empty_cells = np.where(gameboard_copy == 0)
            for Xy, Yy in zip(empty_cells[0], empty_cells[1]):
                gameboard_copy[Xy, Yy] = self.O
                O_values.append(Q_values_dict[str(gameboard_copy)])
                gameboard_copy[Xy, Yy] = 0
            X_values.append(np.mean(O_values))
            gameboard_copy[Xx, Yx] = 0
        Q_values_dict[str(gameboard_copy)] = np.max(X_values)

        return Q_values_dict

    def return_gameboard(self, gameboard) -> np.array:
        """ returns gameboard as visual X O board """
        gameboard_char = np.empty((3, 3), dtype='object')
        for i, row in enumerate(gameboard):
            for j, cell in enumerate(row):
                gameboard_char[i, j] = 'X' if cell == 1 else 'O' if cell == 2 else ''
        return gameboard_char

    def run(self, budget: int):

        for move in range(4):  # 8 total moves, 4 per player

            # player X
            self.player_move_X(budget) # MCTS algo
            X_win, O_win = self.check_if_win(self.gameboard)
            if X_win:
                return self.X, self.return_gameboard(self.gameboard)
            elif O_win:
                return self.O,  self.return_gameboard(self.gameboard)

            # player O
            self.make_random_move_O() # random
            X_win, O_win = self.check_if_win(self.gameboard)
            if X_win:
                return self.X, self.return_gameboard(self.gameboard)
            elif O_win:
                return self.O,  self.return_gameboard(self.gameboard)

        return 0,  self.return_gameboard(self.gameboard)


winner, gameboard = TicTacToe().run(budget=500)

if winner == 0:
    print('draw')
elif winner == 1:
    print('player X has won')
elif winner == 2:
    print('player O has won')
print(gameboard)
