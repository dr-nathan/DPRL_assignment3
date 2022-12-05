#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:46:14 2022

@author: nathanvaartjes
"""

import numpy as np
import copy

class TicTacToe():
    
    def __init__(self):
        #to not get confused, bind X with 1 and O with 2
        self.X = 1
        self.O = 2
        self.turn = 2

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
        self.turn = 1
        
    def player_move_X(self):
        #implement player startegy here
        #for now, random
        empty_cells = np.where(self.gameboard == 0)
        choice = np.random.randint(0, len(empty_cells[0]))
        X, Y = empty_cells[0][choice],  empty_cells[1][choice]
        self.gameboard[X, Y] = self.X
        self.turn = 2
    
    # Return true if one of the players won or if there are no more possible moves
    def check_if_end(self):
        X,O = self.check_if_win()
        return X or O or (len(np.where(node.game_instance.gameboard == 0)[0]) == 0)

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

class Node():
    def __init__(self, instance, parent):
        self.score = 0
        self.game_instance = instance
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

def getQValues(node):
    #if terminal node, 1 reward for winning and 0 for losing
    if node.game_instance.check_if_end():
        node.visits += 1 
        X_win, O_win = node.game_instance.check_if_win()
        if X_win: 
            node.score = 1

        return node.score, node.visits
    
    # for each possible action we create a separate board and save it as a child node
    for action in range(0,len(np.where(node.game_instance.gameboard == 0)[0])):
        new_node = Node(copy.deepcopy(node.game_instance), node)

        empty_cells = np.where(node.game_instance.gameboard == 0)
        X, Y = empty_cells[0][action], empty_cells[1][action]
        # Take the action depending on which players turn it is:
        # Pass the turn to the other player for child nodes
        new_node.game_instance.turn = 1 if node.game_instance.turn == 2 else 2 
        # Make the move according to which players turn it was
        new_node.game_instance.gameboard[X, Y] = node.game_instance.turn 
        node.children.append(new_node)

        # Recursion - backpropagate scores and visits so that they can be used in final
        # argmax calculation to get the best action
        child_Q, child_visits = getQValues(new_node)
        node.score += child_Q
        node.visits += child_visits

    return node.score, node.visits

# Initializing board
starting_gameboard = np.array([[0, 0, 0], 
                               [0, 2, 0], 
                               [0, 0, 0]])

game_instance = TicTacToe()
game_instance.construct_gameboard()
node = Node(copy.deepcopy(game_instance), None) #initial node
node.game_instance.gameboard = starting_gameboard                             
node.game_instance.turn = 1

while True: 
    # If the game ended
    if node.game_instance.check_if_end():
        break
    # if its our turn, determine the optimal move:
    elif(node.game_instance.turn == 1):

        print("-----------------------It's your turn----------------------")
        # print current board:
        print("Current state of the board is: ")
        print(node.game_instance.gameboard)
        print("-----------------------------------------------------------")

        # Update Q values for all nodes:
        print("Calculating QValues...")
        node = Node(copy.deepcopy(node.game_instance), None) #initial node
        getQValues(node)
        
        # Pick best move based on Q value:
        print("Best action according to calculation is:")
        # Pick the best action based on number of winning states/total possible ending states
        # "obj.visits and obj.score/obj.visits" is for handling division by 0
        best_action_node = max(node.children, key=lambda obj: obj.visits and obj.score/obj.visits)
        print(best_action_node.game_instance.gameboard)
        print("\nBest action score (wins out of total possible endings) is: ")
        print(str(best_action_node.score) + " \ " + str(best_action_node.visits))
        print("-----------------------------------------------------------")

        input("Press Enter to take the best action and continue...")
        node = copy.deepcopy(best_action_node)
        node.game_instance.turn = 2
    # If its not our turn, make a random move for the opponent
    else:
        print("\n")  
        print("-----------------It's your opponent's turn-----------------")
        node.game_instance.make_random_move_O()
        print("-----------------------------------------------------------")
        print("-------------Your Opponent made a random move!-------------")
        print("\n")


if node.game_instance.check_if_win()[0] and node.game_instance.check_if_win()[1]:
    print("Draw!")
elif node.game_instance.check_if_win()[0]:
    print("You have won!")
elif node.game_instance.check_if_win()[1]:
    print("Opponent has won!")

