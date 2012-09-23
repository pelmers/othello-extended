#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
AI component of Othello board game
Peter Elmers
"""

import random, sys

# possible sources
HUMAN = 0
RANDOM = 1
SHALLOW = 2
MINIMAX = 3
ALPHABETA = 4

class OthelloAI(object):
    """
    OthelloAI
    """
    def __init__(self, gameObject, side, strat=RANDOM,start="default"):
        self.game = gameObject
        self.side = side
        self.strat = strat
        self.board_start = start
        self.move_count = 0
        # some positions are better, some worse
        self.weights = [
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,120,-20, 20,  5,  5, 20,-20,120,  0,
        0,-20,-40, -5, -5, -5, -5,-40,-20,  0,
        0, 20, -5,  3,  3,  3,  3, -5, 20,  0,
        0,  5, -5,  3,  3,  3,  3, -5,  5,  0,
        0,  5, -5,  3,  3,  3,  3, -5,  5,  0,
        0, 20, -5,  3,  3,  3,  3, -5, 20,  0,
        0,-20,-40, -5, -5, -5, -5,-40,-20,  0,
        0,120,-20, 20,  5,  5, 20,-20,120,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0]

        # is lookup in dicts faster than list?
        # self.weights = dict((k,v) for k,v in enumerate(self.weights))

        #self.weights = dict((pos,5) for pos in range(11,89))
        #for i in [11,18,81,88]:
        #    self.weights[i] = 120
        #for i in [12,22,21,17,27,28,71,72,82,87,77,78]:
        #    self.weights[i] = -50
        #for i in [13,14,15,16,31,41,51,61,38,48,58,68,83,84,85,86]:
        #    self.weights[i] = 25
    
    def random_strat(self):
        """
        Find a move by randomly choosing from all possibilities.
        """
        possible_moves = []
        for pos in range(11,89):
            if self.game.legal_move(pos, self.side):
                possible_moves.append(pos)
        return random.choice(possible_moves) 

    def evaluate_state(self,side):
        """
        Return a score that evaluates the state of the board.
        Uses side to determine which side's point of view to take.
        """
        score = 0
        if self.game.test_end():
            if self.game.find_victor()[0] == side:
                return float("inf") # positive infinity
            elif self.game.find_victor()[0] == -side:
                return float("-inf")  # negative infinity
        for pos in range(11,89):
            if self.game.board[pos] == side:
                score += self.weights[pos]
            elif self.game.board[pos] == -side:
                score -= self.weights[pos]
        return score

    def shallow_search(self):
        """
        Return a move that results in the best outcome immediately following it.
        """
        original_board = self.game.board[:]
        max_score = False
        scores = dict((pos,None) for pos in range(11,89))
        for pos in range(11,89):
           if self.game.make_move(pos,self.side)==False:
               continue
           else:
               score = self.evaluate_state(self.side)
               scores[pos]=score
               self.game.board = original_board[:]
        for pos, score in scores.iteritems():
           if score != None:
               if max_score == False:
                   max_score = score
                   move = pos
               if score > max_score:
                   move = pos
                   max_score = score
        return move

    def maximize(self,ply,side):
        """
        Return the maximum score possible from the current position.
        Use for playing side's move.
        """
        if ply == 0 or self.game.test_end():
            return self.evaluate_state(side) 
        score = float("-inf")
        current_board = self.game.board[:]
        for pos in range(11,89):
            if self.game.make_move(pos,side) == False:
                continue
            self.game.side = side
            score = max(score,self.minimize(ply-1,-side))
            self.game.board = current_board[:]
        return score

    def minimize(self,ply,side):
        """
        Return the lowest score possible from this position.
        Use for opponent's move.
        """
        if ply == 0 or self.game.test_end():
            return self.evaluate_state(side)
        score = float("inf")
        current_board = self.game.board[:]
        for pos in range(11,89):
            if self.game.make_move(pos,side) == False: 
                continue
            self.game.side = side
            score = min(score,self.maximize(ply-1,-side))
            self.game.board = current_board[:]
        return score

    def minimax_search(self,maxply):
        """
        Return a move by using a minimax search to maxply levels deep.
        """
        current_board = self.game.board[:]
        best_score = None
        for pos in range(11,89):
            if self.game.make_move(pos,self.game.side) == False:
                continue
            result_score = self.minimize(maxply,-self.game.side)
            self.game.board = current_board[:]
            self.game.side = self.side
            if best_score is None or result_score > best_score:
                best_score = result_score 
                best_move = pos
        return best_move

    def ab_maximize(self,ply,side,alpha,beta):
        """
        Return the maximum score possible from the current position.
        Use for playing side's move.
        """
        if ply == 0 or self.game.test_end():
            return self.evaluate_state(side)
        current_board = self.game.board[:]
        for pos in range(11,89):
            if self.game.make_move(pos,side) == False:
                continue
            self.game.side = side
            alpha = max(alpha,self.ab_minimize(ply-1,-side,alpha,beta))
            self.game.board = current_board[:]
            if beta <= alpha:
                break
        return alpha

    def ab_minimize(self,ply,side,alpha,beta):
        """
        Return the lowest score possible from this position.
        Use for opponent's move.
        """
        if ply == 0 or self.game.test_end():
            return self.evaluate_state(side)
        current_board = self.game.board[:]
        for pos in range(11,89):
            if self.game.make_move(pos,side) == False: 
                continue
            self.game.side = side
            beta = min(beta,self.ab_maximize(ply-1,-side,alpha,beta))
            self.game.board = current_board[:]
            if beta <= alpha:
                break
        return beta

    def alphabeta_search(self,maxply):
        """
        Return a move by using a minimax search to maxply levels deep.
        """
        current_board = self.game.board[:]
        best_score = None
        for pos in range(11,89):
            if self.game.make_move(pos,self.game.side) == False:
                continue
            result_score = self.ab_minimize(maxply,-self.game.side,-9999,9999)
            self.game.board = current_board[:]
            self.game.side = self.side
            if best_score is None or result_score > best_score:
                best_score = result_score 
                best_move = pos
        return best_move

    def find_move(self):
        """
        Return a move by implementing a strategy determined by the attribute self.strat
        First three moves are random if self.board_start is set
        """
        self.move_count+=1
        if self.board_start == "random" and self.move_count <= 5:
            return self.random_strat()
        if self.strat == RANDOM:
            return self.random_strat()
        elif self.strat == SHALLOW:
            return self.shallow_search()
        elif self.strat == MINIMAX:
            # count the number of empty squares
            # return self.minimax_search(3)
            emptys = sum([1 for i in range(11,89) if self.game.board[i] == self.game.EMPTY])
            # return self.minimax_search(1)
            if emptys < 8:
                # search to the end of the game
                return self.minimax_search(emptys)
            #else:
            return self.minimax_search(3)
        elif self.strat == ALPHABETA:
            emptys = sum([1 for i in range(11,89) if self.game.board[i] == self.game.EMPTY])
            if emptys < 8:
                return self.alphabeta_search(emptys)
            #else:
            return self.alphabeta_search(1)
