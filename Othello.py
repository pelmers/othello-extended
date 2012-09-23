#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
Othello board game, written as part of extended essay
Peter Elmers
"""

import OthelloAI as ai
import sys, time

# screen width for progress bar, assumed 80
WID = 80
HUMAN = 0
RANDOM = 1
SHALLOW = 2
MINIMAX = 3
ALPHABETA = 4

class GameBoard(object):
    """
    GameBoard implements the board itself and methods associated with it
    Handles tasks such as output, move playing, game over conditions,
    listing available moves, scores
    """
    def __init__(self,white_char='O',black_char='X',white_source="human", black_source="human",starting_board="default"):
        self.BORDER=2
        self.EMPTY=0
        # WHITE and BLACK must be opposite integers
        self.WHITE=1
        self.BLACK=-1
        # generate board as list of 100 integers, 8x8 enclosed in 10x10 with borders
        self.board=[self.EMPTY for i in range(100)]
        for i in range(100):
                if (str(i)[-1] == "0" or str(i)[-1] == "9" or i<10 or i>89):
                    self.board[i] = self.BORDER
        self.board[44] = self.board[55] = self.WHITE
        self.board[45] = self.board[54] = self.BLACK
        self.white_char = white_char
        self.black_char = black_char
        self.white_source = white_source
        self.black_source = black_source
        # start AI if it is playing
        if self.white_source != "human":
            self.ai_white = ai.OthelloAI(self,self.WHITE,self.white_source,starting_board)
        if self.black_source != "human":
            self.ai_black = ai.OthelloAI(self,self.BLACK,self.black_source,starting_board)
        self.directions = [1,-1,10,-10,9,-9,11,-11]
        self.side= self.BLACK 
        self.unplayed = 0
        self.last_move = "[no move played yet]"

    def repr_board(self):
        """
        Return a string representing the current board position.
        """
        output = '\t'
        for index,value in enumerate(self.board):
            if 1<=index<=8:
                output += str(index)+' '*3
            elif index%10==0 and index!=0 and index!=90:
                output+=str(index)+'\t'
            elif str(index)[-1] == '9' and index<89:
                output += '\n'+'-'*40+'\n'
            else:
                if value == self.WHITE:
                    output += self.white_char+' '*3
                elif value == self.BLACK:
                    output += self.black_char+' '*3
                elif value == self.EMPTY:
                    output += '-'+' '*3
        scores = self.find_victor()
        output += "\nCurrent score:\nBlack: %s\nWhite: %s" % (scores[2], scores[1])
        return output+'\nLast move was: %s' % (self.last_move)
    
    def flipped_squares(self, move_pos, side):
        """
        Return a list of positions that would be flipped by a tile played at move_pos.
        """
        to_flip = []
        for direction in self.directions:
            next_pos = move_pos + direction
            if self.board[next_pos] == -side:
                flip_this_dir = [next_pos]
                while True:
                    next_pos += direction
                    if (self.board[next_pos] == self.EMPTY) or (self.board[next_pos] == self.BORDER):
                        break
                    if self.board[next_pos] == -side:
                        flip_this_dir.append(next_pos)
                        continue
                    elif self.board[next_pos] == side:
                        to_flip += flip_this_dir
                        break
        return to_flip

    def legal_move(self, move_pos, side):
        """
        Return False if move is not legal.
        Return list of tiles to flip if legal.
        """
        if self.board[move_pos] != self.EMPTY:
            return False
        else:
            flipped = self.flipped_squares(move_pos, side)
            if len(flipped) == 0:
                return False
            else:
                 return flipped
    
    def make_move(self, move_pos, side):
        """
        Try to make a move on the current board.
        Return False if move is illegal.
        If move is legal, return True and make the move.
        """
        to_flip = self.legal_move(move_pos, side)
        if to_flip == False:
            return False
        for pos in to_flip:
            self.board[pos] = side
        self.board[move_pos] = side
        return True

    def get_move(self, side, source="human"):
        """
        Return a move by querying the appropriate source.
        """
        if source == "human":
            while True:
                possible_moves = []
                for pos in range(11,89):
                    if self.legal_move(pos, side):
                        possible_moves.append(str(pos))
                print "Possible moves: %s" % (' '.join(possible_moves))
                try:
                    move = int(raw_input("Enter your move (sum of row and column): "))
                    if str(move) not in possible_moves:
                        print "Invalid move, please try again."
                        continue
                except ValueError:
                    print "Invalid move, please try again."
                    continue
                break
        else:
            if side == self.WHITE:
                move = self.ai_white.find_move()
            if side == self.BLACK:
                move = self.ai_black.find_move()
        return move
    
    def test_possible_moves(self, side):
        """
        Return True if the side has any possible moves.
        If no moves are possible, return False.
        """
        for pos in range(11,89):
            if self.legal_move(pos, side):
                return True
        return False

    def test_end(self):
        """
        Return True if game has ended, else False.
        """
        if self.unplayed == 2:
            return True
        if sum([1 for i in range(11,89) if self.board[i] == self.EMPTY]) == 0:
            return True
        return False
        
    
    def play_turn(self,show=True):
        """
        Handle getting the move from the players, making the move, and going to the next turn.
        Return True if game continues, False if it ends
        """
        if show:
            print self
        if self.test_end() == True:
            return False
        if self.test_possible_moves(self.side) == False:
            self.unplayed += 1
            self.side = -self.side
            return True
        if self.side == self.WHITE:
            move = self.get_move(self.side, self.white_source)
            self.last_move = move
            self.make_move(move,self.side)
        elif self.side == self.BLACK:
            move = self.get_move(self.side, self.black_source)
            self.last_move = move
            self.make_move(move,self.side)
        self.side = -self.side
        self.unplayed = 0
        return True

    
    def find_victor(self):
        """
        Find the winner and scores of each player of the game.
        Assume that the game is finished.
        """
        white_count = sum([1 for i in range(11,89) if (self.board[i]==self.WHITE)])
        black_count = sum([1 for i in range(11,89) if (self.board[i]==self.BLACK)])
        if white_count > black_count:
            return self.WHITE, white_count, black_count
        elif black_count > white_count:
            return self.BLACK, white_count, black_count
        elif white_count == black_count:
            return self.EMPTY, white_count, black_count

    def __str__(self):
        # lets us do 'print self' to simplify showing board
        return self.repr_board()

def progress_bar(width, percent, char='#'): # to show simulation progress
    """
    Progress bar with variable width, scales percentage to width
    Example: [ ####------ ] 42%
    """
    if width < 10:
        return 'bad width'
    width += -7
    width += -len(str(percent))
    filled = int(round((float(width)*(float(percent)/100))))
    return '\r[ %s%s ] %i ' % (
    char[0:1]*filled, '-'*(width-filled), percent) + r'%'

def menu(choices_list,message):
    choices_dict = dict(enumerate(choices_list))
    for k,v in choices_dict.items():
        print "%s) %s" % (k+1,v)
    return int(raw_input(message))-1
    print "%s selected" % (choice)
    return choice


def main():
    sources = ['Human','Random','Shallow searcher (1-ply)','Brute Minimax (3-ply)','Alphabeta pruning (3-ply)']
    black_source = menu(sources,"Source for black player: ")
    white_source = menu(sources,"Source for white player: ")
    sim_number = 0
    if white_source != HUMAN and black_source != HUMAN:
        if raw_input("Do you want to simulate games? [Y/n] ") in ['y','Y','yes',"Yes"]:
            sim_number = int(raw_input("How many games to simulate? "))
            randomize = raw_input("Do you want to randomize game starts? ")
            if randomize in ['y','Y','yes','Yes']:
                randomize = "random"
            else:
                randomize = "default"
            output = '\n'
    if sim_number == 0:
        # non-simulation portion of main()
        game = GameBoard(white_source=white_source, black_source=black_source)    
        Playing = True
        while Playing:
            Playing = game.play_turn()
        victor,whites,blacks = game.find_victor()
        if victor == game.WHITE:
            print "White has won with a score of %s to %s" % (whites, blacks)
        if victor == game.BLACK:
            print "Black has won with a score of %s to %s" % (blacks, whites)
        if victor == game.EMPTY:
            print "The game is tied with a score of %s to %s" % (whites, blacks)
    else:
        # simulation processing and output
        percent = None
        black_wins = 0
        white_wins = 0
        draws = 0
        Start = time.clock()
        # ready, set, go!
        for sim in range(sim_number):
            new_percent = round(float(sim)/float(sim_number),2)*100
            if new_percent != percent or percent is None:
               sys.stdout.write(progress_bar(WID, new_percent)) 
               sys.stdout.flush()
               percent = new_percent
            game = GameBoard(white_source=white_source, black_source=black_source,starting_board=randomize)
            Playing = True
            while Playing:
                Playing = game.play_turn(show=False)
            victor, whites, blacks = game.find_victor()
            if victor == game.WHITE:
                output += "White wins %s to %s \n" % (whites, blacks)
                white_wins += 1
            elif victor == game.BLACK:
                output += "Black wins %s to %s \n" % (blacks, whites)
                black_wins += 1
            else:
                output += "Game tied %s to %s \n" % (whites, blacks)
                draws += 1
        End = time.clock()
        print output
        print "Black %s\nWhite %s\nDraw %s" % (str(round(float(black_wins)/float(sim_number),3)*100)+r'%',
            str(round(float(white_wins)/float(sim_number),3)*100)+r'%', str(round(float(draws)/float(sim_number),3)*100)+r'%')
        print "Simulation lasted %.3f seconds, %.3f seconds per game." % ((End-Start),(End-Start)/sim_number)


if __name__ == '__main__':
    main()
