#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:46:14 2022

@author: nathanvaartjes
"""

import numpy as np

class TicTacToe():
    
    def __init__(self):
        #to not get confused, bind X with 1 and O with 2
        self.X = 1
        self.O = 2
        
    def construct_gameboard(self):
        # 0 is empty, 1 is X, 2 is O
        self.gameboard = np.zeros((3,3))
        self.gameboard[1,1] = self.O
        
    def make_random_move_O(self):
        #get empty cells
        empty_cells = np.where(self.gameboard == 0)
        #choose 1 empty cell
        choice = np.random.randint(0, len(empty_cells[0]))
        #get coordinates of schosen cell and put O
        X, Y = empty_cells[0][choice],  empty_cells[1][choice]
        self.gameboard[X, Y] = self.O
        
    def player_move_X(self):
        #implement player startegy here
        #for now, random
        empty_cells = np.where(self.gameboard == 0)
        choice = np.random.randint(0, len(empty_cells[0]))
        X, Y = empty_cells[0][choice],  empty_cells[1][choice]
        self.gameboard[X, Y] = self.X
        
    def check_if_win(self) -> (bool, bool): #returns X_win, O_win
        #check rows
        for row in self.gameboard:
            if np.all(row == self.X):
                return True, False
            elif np.all(row == self.O):
                return False, True
        #check columns
        for column in self.gameboard.T:
            if np.all(column == self.X):
                return True, False
            elif np.all(column == self.O):
                return False, True
        #check diagonals:
        for diag in np.diag(self.gameboard), np.diag(np.fliplr(self.gameboard)):
            if np.all(diag == self.X):
                return True, False
            elif np.all(diag == self.O):
                return False, True    
            
        return False, False
        
    def return_gameboard(self) -> np.array :
        gameboard_char = np.empty((3,3), dtype = 'object')
        for i, row in enumerate(self.gameboard):
            for j, cell in enumerate(row):
                gameboard_char[i,j] = 'X' if cell==1 else 'O' if cell==2 else ''
        return gameboard_char
    
    def run(self):
        
        self.construct_gameboard()
        
        for move in range(4): #8 total moves, 4 per player
            
            #player X
            self.player_move_X()
            X_win, O_win = self.check_if_win()
            if X_win:
                return self.X, self.return_gameboard()
            elif O_win: 
                return self.O,  self.return_gameboard()
            
            #player O
            self.make_random_move_O()
            X_win, O_win = self.check_if_win()
            if X_win:
                return self.X, self.return_gameboard()
            elif O_win: 
                return self.O,  self.return_gameboard()
            
        return 0,  self.return_gameboard()
            
winner, gameboard = TicTacToe().run()
if winner ==0:
    print('draw')
elif winner ==1:
    print('player X has won')    
elif winner ==2:
    print('player O has won')    
print(gameboard)