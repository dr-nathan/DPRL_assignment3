#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 13:46:14 2022

@author: nathanvaartjes
"""

import numpy as np
import copy
import random
import math

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
        return X or O or (len(np.where(self.gameboard == 0)[0]) == 0)

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
        self.game_instance = instance
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

# If the node has children we pick the one that is most suited according to calculateScore()
def selectNode(root_node):
    node = root_node
    while (len(node.children) != 0):
        node = selectBestNode(node)
    
    return node

def selectBestNode(node):
    best_child = max(node.children, key=lambda obj: calculateScore(node.visits, obj.wins, obj.visits))
    return best_child

# TODO explain this function but basically we take the most winning state while also considering
# total visits, if node has no visits we encourage the algorithm to visit it
def calculateScore(parent_visit_count, wins, visit_count) -> float:
    if (visit_count == 0):
        return 9999999999
    return float(wins/visit_count) + 1.41 * math.sqrt(math.log(parent_visit_count/visit_count))

def expandNode(node):
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
    return

# Simulate a game from the chosen node, if we win return True if not False
def simulateRandomPath(node):
    tempNode = Node(copy.deepcopy(node.game_instance), node.parent)
    # While the game has not ended
    while not tempNode.game_instance.check_if_end():
        if tempNode.game_instance.turn == 1:
            tempNode.game_instance.player_move_X()
        else:
            tempNode.game_instance.make_random_move_O()

    X_win, O_win = tempNode.game_instance.check_if_win()
    if X_win: 
        return True
    else:
        return False

# Backpropagate visits and wins back up until the root node
def backpropagate(leaf_node, win):
    node = leaf_node
    while node is not None:
        node.visits += 1
        #if node.game_instance.turn == 1 and win:
        if win:
            node.wins += 1
        node = node.parent
    return

# Initializing board
starting_gameboard = np.array([[0, 0, 0], 
                               [0, 2, 0], 
                               [0, 0, 0]])

game_instance = TicTacToe()
game_instance.construct_gameboard()
node = Node(copy.deepcopy(game_instance), None) #initial node
node.game_instance.gameboard = starting_gameboard                             
node.game_instance.turn = 1

def calculate_best_move(node):
    for i in range(0, 1000):
        selected_node = selectNode(node)

        # print("before expand:")
        # print(len(selected_node.children))
        if not selected_node.game_instance.check_if_end():
            expandNode(selected_node)
        
        # print("After expand:")
        # print(len(selected_node.children))
        # We select a node with the best score and if it has any children we build out the tree
        node_to_explore = selected_node
        if (len(node_to_explore.children) > 0):
            node_to_explore = random.choice(selected_node.children)

        random_path_win = simulateRandomPath(node_to_explore)
        # print(random_path_win)
        backpropagate(node_to_explore, random_path_win)


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

        # Update Q values for all child nodes to determine best move:
        print("Calculating QValues...")
        calculate_best_move(node)
        
        print("The different next steps (actions) that we can take have the following stats: ")
        for children in node.children:
            print("Gameboard:")
            print(children.game_instance.gameboard)
            print("the node has been visited: " + str(children.visits) + " times")
            print("a total of : " + str(children.wins) + " times this action resulted in a win")

        print("-----------------------------------------------------------")
        # Pick the best action based on number of visits - because of how selectBestNode()
        # works the child with the most visits is bound to be the best choice because
        # it resulted in the most winning leaf nodes when compared to the total visits
        best_action_node = max(node.children, key=lambda obj: obj.visits)

        print("The action that results in the most wins is:")
        print(best_action_node.game_instance.gameboard)
        print("-----------------------------------------------------------")

        input("Press Enter to take the best action and continue...")
        node = Node(copy.deepcopy(best_action_node.game_instance), None)
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

