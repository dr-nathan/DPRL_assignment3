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

from matplotlib import pyplot as plt


class TicTacToe:

    def __init__(self):
        # to not get confused, bind X with 1 and O with 2
        self.X = 1
        self.O = 2

        # 0 is empty, 1 is X, 2 is O
        self.gameboard = np.zeros((3, 3))
        self.gameboard[1, 1] = self.O

    def make_random_move_O(self):
        # get empty cells
        empty_cells = np.where(self.gameboard == 0)
        # choose 1 empty cell
        choice = np.random.randint(0, len(empty_cells[0]))
        # get coordinates of schosen cell and put O
        X, Y = empty_cells[0][choice],  empty_cells[1][choice]
        self.gameboard[X, Y] = self.O
        self.turn = 1
        
    def player_move_X(self):
        # implement player startegy here
        # for now, random
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
        # check columns
        for column in self.gameboard.T:
            if np.all(column == self.X):
                return True, False
            elif np.all(column == self.O):
                return False, True
        # check diagonals:
        for diag in np.diag(self.gameboard), np.diag(np.fliplr(self.gameboard)):
            if np.all(diag == self.X):
                return True, False
            elif np.all(diag == self.O):
                return False, True

        return False, False

    def return_gameboard(self) -> np.array:
        gameboard_char = np.empty((3, 3), dtype='object')
        for i, row in enumerate(self.gameboard):
            for j, cell in enumerate(row):
                gameboard_char[i, j] = 'X' if cell == 1 else 'O' if cell == 2 else ''
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
    best_child = max(node.children, key=lambda obj: calculateUCTScore(node.visits, obj.wins, obj.visits))
    return best_child


# TODO explain this function but basically we take the most winning state while also considering
# total visits, if node has no visits we encourage the algorithm to visit it
def calculateUCTScore(parent_visit_count, wins, visit_count) -> float:
    c = 1.2 # Temperature
    if (visit_count == 0):
        return 9999999999
    return float(wins)/float(visit_count) + c * math.sqrt(math.log(float(parent_visit_count)/float(visit_count)))


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
    return node


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
        #print("WON")
        return True
    else:
        return False


# Backpropagate visits and wins back up until the root node
def backpropagate(leaf_node, win):
    node = leaf_node
    while node is not None:
        node.visits += 1
        # if node.game_instance.turn == 1 and win:
        if win:
            node.wins += 1
        else:
            node.wins -= 1
        node = node.parent
    return


def calculate_best_move(node, simulations_per_move):
    # Simulate x games to calculate Q values
    for i in range(0, simulations_per_move):

        selected_node = selectNode(node)

        if not selected_node.game_instance.check_if_end():
            selected_node = expandNode(selected_node)
        
        # We select a node with the best score and if it has any children we build out the tree
        node_to_explore = selected_node
        if len(node_to_explore.children) > 0:
            node_to_explore = random.choice(selected_node.children)

        random_path_win = simulateRandomPath(node_to_explore)
        backpropagate(node_to_explore, random_path_win)


def get_best_move_value(node, turn):
    # Get the best move from the root node, recusrively go through the tree
    if node.game_instance.check_if_end():
        return 1 if node.game_instance.check_if_win()[0] else 0
    if turn == 1:
        if any(node.children):
            # get maximum of children nodes if X turn
            value = np.max([get_best_move_value(child, 2) if child.visits > 0 else 0 for child in node.children])
        else:
            value = 0
    else:
        if any(node.children):
            # get average of children nodes if O turn
            value = np.mean([get_best_move_value(child, 1) if child.visits > 0 else 0 for child in node.children])
        else:
            value = 0
    return value


def run_game(interactive : bool, simulations_per_move : int):
    # Initializing game and make board
    game_instance = TicTacToe()

    state_scores = []

    node = Node(copy.deepcopy(game_instance), None)  # initial node
    node.game_instance.turn = 1

    while True: 
        # If the game ended
        if node.game_instance.check_if_end():
            break
        # if its our turn, determine the optimal move:
        elif(node.game_instance.turn == 1):

            if interactive:
                print("-----------------------It's your turn----------------------")
                # print current board:
                print("Current state of the board is: ")
                print(node.game_instance.return_gameboard())
                print("-----------------------------------------------------------")

                # Update Q values for all child nodes to determine best move:
                print("Calculating QValues...")

            calculate_best_move(node, simulations_per_move)
            if interactive:

                print("The different next steps (actions) that we can take have the following stats: ")
                for children in node.children:
                    print("Gameboard:")
                    print(children.game_instance.return_gameboard())
                    print("this node has been visited: " + str(children.visits) + " times")
                    print("a total of : " + str(children.wins) + " times this action resulted in a win")
                    print(f"the MCTS algorithm scores it with an {get_best_move_value(children, 1)}")

                print("-----------------------------------------------------------")
                # Pick the best action based on number of visits - because of how selectBestNode()
                # works the child with the most visits is bound to be the best choice because
                # it resulted in the most winning leaf nodes when compared to the total visits
            best_action_node = max(node.children, key=lambda obj: get_best_move_value(obj, 1))
            state_scores.append(get_best_move_value(best_action_node, 1))

            #best_action_node = max(node.children, key=lambda obj: obj.visits)
            if interactive:
                print("The action that results in the most wins is:")
                print(best_action_node.game_instance.return_gameboard())
                print("-----------------------------------------------------------")

                input("Press Enter to take the best action and continue...")
            node = Node(copy.deepcopy(best_action_node.game_instance), None)
            node.game_instance.turn = 2

        # If its not our turn, make a random move for the opponent
        else:
            node.game_instance.make_random_move_O()
            if interactive:
                print("\n")  
                print("-----------------It's your opponent's turn-----------------")
                print("-----------------------------------------------------------")
                print("-------------Your Opponent made a random move!-------------")
                print("\n")

    if interactive:
        if node.game_instance.check_if_win()[0] and node.game_instance.check_if_win()[1]:
            print("Draw!")
        elif node.game_instance.check_if_win()[0]:
            print("You have won!")
        elif node.game_instance.check_if_win()[1]:
            print("Opponent has won!")
    else:
        # pad scores with final score to make sure that the length of the list is always the same
        if len(state_scores) < 4:
            state_scores.extend([node.game_instance.check_if_win()[0]*1]*(4-len(state_scores)))
        return node.game_instance.check_if_win(), state_scores


state_scores = []
wins, loses, draws = 0, 0, 0
games_to_play = 100
simulations = 2000

for i in range(0, games_to_play):
    if i % 10 == 0:
        print(str(i) + " games simulated")

    (X, O), state_scores_run = run_game(interactive=False, simulations_per_move=simulations)
    state_scores.append(state_scores_run)
    if not X and not O:
        draws += 1
    elif X:
        wins += 1
    else:
        loses += 1

print("Statistics after simulating " + str(games_to_play) + " games total with " + str(simulations) +
      "randomly simulated paths every (player) turn:")
print("Total wins:" + str(wins))
print("Total loses:" + str(loses))
print("Total draws:" + str(draws))

mean_scores = np.array(state_scores).mean(axis=0)
std_scores = np.array(state_scores).std(axis=0, ddof=1)

plt.errorbar([1, 2, 3, 4], mean_scores, yerr=mean_scores / 2)
plt.title("MCTS score per turn")
plt.xlabel("Turn")
plt.ylabel("MCTS score")
plt.show()