#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GameClasses.py

This module contains the data structures (the chessboard state, players, and associated data) and their methods.
"""

""" Imports """
## Python Library Imports
from collections import namedtuple, deque
from itertools import islice
from numpy import inf
from random import choice
from re import split

## Source code imports
import GameUtils

""" Global Variables """

### ANSI Escape Codes ###
# Gives the board a checkered pattern like a real chessboard
bw = '\x1b[47m' # Background white
bb = '\x1b[40m' # Background black
fw = '\x1b[37m' # Foreground white
fb = '\x1b[30m' # Foreground black
fr = '\x1b[39m' # Foreground reset
br = '\x1b[49m' # Background reset

""" Classes """

class Player(object):
    """
    Player class is used to represent the owner of the pieces and who is making the moves in the game.
    """
    def __init__(self, name, input_mode=False):
        """
        Initializer for the player class.
            Arguments:
                name -- a string containing the name of the player. Must either be 'X' or 'Y'.
                input_mode -- a Boolean value indicating whether the player will use moves from input (for competition mode). Default value is set to False.
        """
        # Assert that player was correctly initialized with a valid name
        assert name.upper() in ['X', 'Y'], 'Player name must be either X or Y.'
        assert type(input_mode) is bool
        
        # Set-up instance attributes for the player
        self.name = name.upper()
        self.input_mode = input_mode
        self.ply = 4
        self.state_deque = deque()
    
    def __str__(self):
        """
        Overrides the base method to produce a custom string representation for the class by simply returning 'Player X' or 'Player Y'.
        """
        return 'Player ' + self.name
        
    """ METHODS """
    
    def parse_position(self, ordered_pair):
        """
        Parses an ordered pair for making a move. Note: externally, the positions are considered as having row and column values 1-8.
        This function deducts a value of 1 to make them 0-7 in order to align the values with list indices since Python uses zero-based numbering.
            Arguments:
                ordered_pair -- a string in the format of K(x,y). The first letter must be K or R to represent a rook or king.
            Returns:
                the requested piece and its position, or None if invalid syntax was entered.
        """
        # Split the input where there are parentheses or a comma; these should be the only delimiters in the input
        strs = split('[(,)]', ordered_pair)
        # Filter out empty values
        strs = filter(None, strs)
        # strs is a list of split strings and should contain 3 strings:
            # Piece name
            # X coordinate
            # Y coordinate
        if len(strs) == 3:
            # If the first string is K
            f, r = GameUtils.check_coordinates(strs[1], strs[2])
            if strs[0].upper() == 'K':
                return King(self, Position(f, r))
            elif strs[0].upper() == 'R' and self.name == 'X':
                return Rook(self, Position(f, r))

    def move(self, current_state):
        """
        This method is intended to wrap the two possible ways of moving into one: from user input (in competition mode) or from searching the game tree.
        If the current instance's input_mode is set to True, it will use the method self._play_from_move(current_state) to get user input for making a move.
        Otherwise, it will use the method self._play_from_tree(current_state) to pick a move using the alpha-beta pruning mini-max algorithm.
            Arguments:
                current_state -- the current state produced either by initialization of a game or by the oppponent's turn. Should be an instance of GameState.
            Returns:
                a child node representing the move made, which will depend on which type of player the current instance is.
        """
        # Assert that self (this instance of player) is one of the players in the game
        assert self is current_state.current_player
        # Assert that the given argument current_state is an instance of the class GameState
        assert isinstance(current_state, GameState), 'current_state must be an instance of class GameState'
        self.state_deque.appendleft(current_state)
        # Pick the correct method of making a move based on input_mode
        if self.input_mode:
            return self._input_move(current_state)
        else:
            return self._minimax_move(current_state)
    
    def heuristic(self, state, depth):
        """
        Returns the heuristic value of the given state and depth (relative to the current game state) based on the current player.
            Arguments:
                state -- an instance of GameState for which the heuristic function is evaluated.
                depth -- the distance of the given state from the current game state as given by the mini-max algorithm.
        """        
        # Return the heuristic value based on the player
        if self.name == 'X':
            return self._heuristic_x(state, depth)
        else:
            return self._heuristic_y(state, depth)
    
    def alphabeta_search(self, state):
        """
        Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function.
        Adapted (and modified) from: http://aima.cs.berkeley.edu/python/games.html
            Arguments:
                state - the state node representing the current game state.
            Returns:
                child - a game state representing the node chosen by the alpha-beta mini-max search algorithm.
        """

        ## Nested functions for assessing MAX and MIN nodes ##
        def max_value(state, alpha, beta, depth):
            """
            Alpha-beta pruning for MAX nodes
                Arguments:
                    state -- the current state
                    alpha -- the depth from the root node
                    beta -- the beta level
                    depth -- the alpha level
                Returns:
                    heuristic value
            """
            if state.is_leaf or depth >= self.ply or (self.name == 'X' and state.check_cycle(min_length=4,max_length=8)):
                return (state, self.heuristic(state, depth))
            v = -inf
            for child in state.children:
                v = max(v, min_value(child, alpha, beta, depth+1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v
    
        def min_value(state, alpha, beta, depth):
            """
            Alpha-beta pruning for MIN nodes
                Arguments:
                    state -- the current state
                    alpha -- the depth from the root node
                    beta -- the beta level
                    depth -- the alpha level
                Returns:
                    heuristic value
            """
            if state.is_leaf or depth >= self.ply:
                return self.heuristic(state, depth)
            v = inf
            for child in state.children:
                v = min(v, max_value(child, alpha, beta, depth+1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v
    
        ## Search is actually initiated through calling a lambda function of min_value on
        ## the current state's children, since the root node will always be MAX
        alpha_beta = lambda child: min_value(child, -inf, inf, 0)
        
        # This is the major bottleneck of the program, so a KeyboardInterrupt exception handler
        # has been put here to deal make sure the user is sure before exiting the program for good.
        while True:
            try:
                # This is where the alpha-beta function is actually called
                child_values = [(alpha_beta(child), child) for child in state.children]
                break
            except KeyboardInterrupt:
                # Handles KeyboardInterrupt
                condition = lambda r: r.upper() in ['YES','Y','NO','N']
                response = GameUtils.query_until('\nGame interrupted!!! If you choose not to continue, the game will terminate. \nOtherwise, it will restart the last search. Continue with the game? (Y/N)', condition)
                if response.upper() in ['N','NO']:
                    response = GameUtils.query_until('\nThere may be other games (if this is test mode), would you like to continue to the next game? (Y/N)', condition)
                    if response.upper() in ['Y','YES']:
                        return
                    else:
                        print 'Exiting...'
                        exit(0)
        # Sort children in non-increasing order of heuristic value
        child_values.sort(key=lambda tup: tup[0], reverse=True)
        winners = []
        max_val = -inf
        # Iterate through each to see if there are multiple winners
        for (hval, child) in child_values:
            if hval >= max_val:
                max_val = hval
                winners.append(child)
            else:
                # Breaks out of iteration when heuristic value decreases
                break
        # Make sure a child state is chosen, otherwise we have a serious problem
        assert len(winners) != 0, 'No winners picked!!!'
        # Randomly select a child from the list if necessary
        child = choice(winners)
        state.cleanup(child)
        return child
            
    ## Private methods
    def _minimax_move(self, current_state):
        """
        This method makes a move for the player as AI based off of the current game state. Only intended to be called by the self.move method.
            Arguments:
                current_state -- the game state returned by the last player, representing the current state of the game.
            Returns:
                a child node resulting from the move picked by the alpha-beta pruning mini-max algorithm.
        """
        # Checking the current state's game status
        game_status = current_state.game_status
        # Returns the next move only if the game status is OK, otherwise returns None
        if game_status in ['continue', 'check']:
            return self.alphabeta_search(current_state)
    
    def _input_move(self, current_state):
        """
        This method allows user input to make a move so that someone else (a person or a program) can play against this program. Only intended to be called by the self.move method.
            Arguments:
                current_state -- the game state returned by the last player, representing the current state of the game.
            Returns:
                a child node resulting from the move that was given.
        """        
        # Checking the current state's game status
        game_status = current_state.game_status
        # Returns the next move only if the game status is OK, otherwise returns None
        if game_status in ['continue', 'check']:
            # Queries the user to input a move. Formatting examples: K(1,2), R(5,2), etc.
            legal_move = lambda piece: piece in current_state.legal_moves
            move = GameUtils.query_until_parsed('Please enter the piece and the position you would like to move it to (e.g., K(1,2)):', self.parse_position, condition=legal_move)
            return current_state.child_from_move(move)
           
    def _heuristic_x(self, state, depth):
        """
        A private method that returns the heuristic value of player x in the given instance of GameState.
        Intended to be called from the heuristic(state, depth) method.
            Arguments:
                state -- an instance of GameState for which the heuristic function is evaluated.
                depth -- the distance of the given state from the current game state as given by the mini-max algorithm.
        """
        # Get the positions of the three pieces on the chess board in the current state
        KX_position = state.KX.position
        RX_position = state.RX.position
        KY_position = state.KY.position
        
        # Initialize values for bonus and penalty
        bonus = 0
        penalty = 0
        
        # Count the number of attacking positions KY has. The more it has, the more deduction from the heuristic value.
        # The deduction gets reduced as KY moves away from the center or gets blocked by the rook
        KY_moves = filter(state.king_filter(state.KY), state.y_attacking_positions)
        KY_moves_n = len(KY_moves)
        # Center Manhattan distance of KY
        KY_cmd = GameUtils.cent_man_dist(KY_position)
        RX_cmd = GameUtils.cent_man_dist(RX_position)

        # Got to avoid cycles!
        if state.check_cycle(min_length=4, max_length=8):
            penalty += 1000
        
        # Allot bonus/penalties based on game status
        if state.game_status == 'checkmate':
            bonus += 1000/float(depth+1)
        elif state.game_status in ['stalemate', 'insufficient materials']:
            penalty += 1000/float(depth+1)
        
        if state.current_player is state.player_y:
            # Allot penalty for moving rook to a space where the king can take it out
            if GameUtils.chesbyshev_distance(KY_position, RX_position) == 1:
                penalty += 1000
            # Small bonus for pushing the King against the opposing King
            if GameUtils.chesbyshev_distance(KY_position, KX_position) == 2:
                bonus += 20
                
        # Absolute difference between the x and y distances of RX and KY
        # The larger the better --> this indicates that the king is more vulnerable to the rook
        RX_KY_df = abs(KY_position.file - RX_position.file)
        RX_KY_dr = abs(KY_position.rank - RX_position.rank)
        RX_KY_test = (max(RX_KY_df, RX_KY_dr)/float(min(RX_KY_df, RX_KY_dr)+1))-1
        if state.KX.between(RX_position, KY_position):
            # But this should be punished if KX is blocking because this protects KY
            RX_KY_test = -2*RX_KY_test
        # Manhattan distance between KX and KY
        KX_KY_man = GameUtils.man_dist(KX_position,KY_position)
        
        return 9.7*KY_cmd + 1.6*(14 - KX_KY_man) + RX_KY_test - (10*KY_moves_n/float(KY_cmd+1)) + bonus - penalty

    def _heuristic_y(self, state, depth):
        """
        A private method that returns the heuristic value of player y in the given instance of GameState.
        Intended to be called from the heuristic(state, depth) method.
            Arguments:
                state -- an instance of GameState for which the heuristic function is evaluated.
                depth -- the distance of the given state from the current game state as given by the mini-max algorithm.
        """
        # Get the positions of the three pieces on the chess board in the current state
        KX_position = state.KX.position
        RX_position = state.RX.position
        KY_position = state.KY.position
        
        # Initialize values for bonus and penalty
        bonus = 0
        penalty = 0
        
        # Allot bonus for checkmate
        if state.game_status == 'checkmate':
            penalty += 1000/float(depth+1)
        elif state.game_status in ['stalemate', 'insufficient materials']:
            bonus += 1000/float(depth+1)    
            
        # Allot penalty for rook having same row or column as king, aka "check" or "checkmate"
        if state.piece_under_attack(state.KY):
            penalty += 500
            
        # Bonus for offensive moves
        if state.current_player is state.player_x:
            if GameUtils.chesbyshev_distance(KY_position, RX_position) == 1:
                #print 'bonus given to player y for having king posted near rook X'
                bonus += 250
            if GameUtils.chesbyshev_distance(KY_position, KX_position) == 2:
                #print 'bonus given to player y for having king posted near king X'
                bonus += 10
        
        # Count the number of legal moves KY has. The more moves it has, the greater the heuristic value.
        # This addition is worth less if KY moves away from center of the board
        KY_moves = len(filter(state.king_filter(state.KY), state.y_attacking_positions))
        
        # Center Manhattan distance for KY
        KY_cmd = GameUtils.cent_man_dist(KY_position)
        
        # Absolute difference between the x and y distances of RX and KY
        # The closer to zero the better --> this indicates that the king is less vulnerable to the rook
        RX_KY_diff = abs(abs(KY_position.file - RX_position.file) - abs(KY_position.rank - RX_position.rank))
        
        return -9.3*RX_KY_diff - 5.7*KY_cmd + (10*KY_moves/float(KY_cmd+1)) + penalty - bonus
    
### Chess Piece Classes ###
class Position(namedtuple('Position', ['file','rank'])):
    def __sub__(self, other):
        assert isinstance(other,Position)
        return (other.file-self.file, other.rank-self.rank)
    
    @classmethod
    def is_valid(cls, f, r):
        """
        Class method to check if a given file and rank are valid for a position.
        """
        for i in (f,r):
            if i < 1 or i > 8:
                return False
        return True
    
""" PIECE CLASSES """    
class Rook(object):
    """
    A class representing rooks.
    """
    def __init__(self, owner, position):
        """
        Constructor for instances of the class Rook.
            Arguments:
                owner -- an instance of Player to represent the owner of the piece.
        """
        self.owner = owner
        self.position = position
        self.attacking_positions = self._get_attacking_positions()
    
    def __str__(self):
        return 'R' + self.owner.name
    
    def __repr__(self):
        return self.__str__() + '(%i,%i)' % (self.position.file, self.position.rank)
    
    def move(self, new_position):
        """
        Move the current instance of Rook to a specified position.
            Arguments:
                new_position -- an instance of position specifying where to move the rook to
            Returns:
                new_rook -- a new rook with the specified position.
        """
        new_rook = Rook(self.owner, new_position)
        return new_rook
  
    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.position == self.position
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def _get_attacking_positions(self):
        """
        A private method used to set the attacking_positions attribute for the rook. Called upon initialization.
            Arguments:
                None
            Returns:
                attacking positions
        """
        current_file, current_rank = self.position
        hor = [Position(f, current_rank) for f in xrange(1,9) if f != current_file]
        ver = [Position(current_file, r) for r in xrange(1,9) if r != current_rank]
        return hor + ver

class King(object):
    """
    A class representing kings.
    """
    directions = {
        # A dict containing the directions which the king can move.
        # The keys are acronyms for North, Northwest, South, Southwest, etc.
        # The values are the corresponding x and y changes in position on the board.
        'NW': (-1,-1),
        'SW': (-1,1),
        'SE': (1,1),
        'NE': (1,-1),
        'N': (0,-1),
        'W': (-1,0),
        'S': (0,1),
        'E': (1,0)
    }
    def __init__(self, owner, position):
        """
        Constructor for instances of the class King.
            Arguments:
                owner -- an instance of Player to represent the owner of the piece.
        """
        self.owner = owner
        self.position = position
        self.attacking_positions = self._get_attacking_positions()
        
    def __str__(self):
        """
        String formatting for objects of class King. Used for printing on the board
        """
        return 'K' + self.owner.name
    
    def __repr__(self):
        """
        String representation for objects of class King. Used for debugging purposes.
        """
        return self.__str__() + '(%i,%i)' % (self.position.file, self.position.rank)
    
    def __eq__(self, other):
        """
        Overriding the == operator for class King to ensure it works properly.
        """
        return isinstance(other, self.__class__) and other.position == self.position
    
    def __ne__(self, other):
        """
        Overriding the != operator for class King to ensure it works properly.
        """
        return not self.__eq__(other)
    
    """ METHODS """
    def move(self, new_position):
        """
        Creates a "move" by generating a king at a new position.
            Arguments:
                new_position -- an instance of Position for the location of the move
            Returns:
                new_king -- an instance of King at new_position
        """
        new_king = King(self.owner, new_position)
        return new_king
    
    def between(self, p1, p2):
        """
        Tests if the king is between two other pieces.
            Arguments:
                p1 -- a position
                p2 -- a second position
            Returns:
                Boolean value indicating whether the king is situated directly between the two given positions (p1 and p2)
        """
        king_pos = self.position
        # If the three pieces are aligned in a file together
        if king_pos.file == p1.file and king_pos.file == p2.file:
            # Check to see if the current king is in the middle
            if (p1.rank < king_pos.rank and king_pos.rank < p2.rank) or (p1.rank > king_pos.rank and king_pos.rank > p2.rank):
                return True
        # If the three pieces are aligned in a rank together
        if king_pos.rank == p1.rank and king_pos.rank == p2.rank:
            # Check to see if the current king is in the middle
            if (p1.file < king_pos.file and king_pos.file < p2.file) or (p1.file > king_pos.file and king_pos.file > p2.file):
                return True        
        # If these tests fail, then the king is not in the middle of the pieces
        return False
    
    def _get_attacking_positions(self):
        """
        A private method used to set the attacking_positions attribute for the king. Called upon initialization.
            Arguments:
                None
            Returns:
                attacking positions
        """        
        # Get current x and y coordinates
        f, r = self.position
        # List comprehension to return each possible attacking position
        return [Position(f+df, r+dr) for df, dr in King.directions.values() if Position.is_valid(f+df, r+dr)]

### Board Structure ###
class Board(object):
    """
    A class to represent the chess board in a 2-dimensional array.
    """
    def __init__(self, pieces=None):
        """
        Constructor for instances of the class Board.
            Arguments:
                pieces -- a list of pieces to immediately add to the board. Default value is set to None.
            Returns:
                None
        """
        # Create the board size: 8x8 array
        board_range = range(8)
        self._mat = [[None for x in board_range] for x in board_range]
        # If the constructor is called with pieces to add, the following code will execute to immediately add them.
        if pieces is not None:
            self._add_pieces(pieces)
        
    def __str__(self):
        """
        Overriding the base function str() to customize its behavior for instances of class Board.
        This method constructs a string representation of the chessboard based on the pieces in it.
        """        
        # The string representing the top of each row
        top_even = '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|\n'
        top_odd = '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|' + bb + '‾‾‾‾‾‾' + br + '|' + bw + '‾‾‾‾‾‾' + br + '|\n'
        # The string representing the bottom of each row
        bot_even = '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|\n'
        bot_odd = '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|' + bb + '______' + br + '|' + bw + '______' + br + '|\n'
        # Initializing an empty string which will be returned as the final string
        board_str = ''
        # Initializing the row number to be included as part of the board string
        row_n = 0
        for row in self._mat:
            # Initializing the string representing the middle section of each row
            mid = ''
            for i in xrange(len(row)):
                # If there is no piece in the current position
                if row[i] is None:
                    # concatenate a string representing the middle an empty cell to the mid string.
                    if (row_n%2 == 0 and i%2 == 0) or (row_n%2 == 1 and i%2 == 1):
                        mid += '|' + bw + '      ' + br
                    else:
                        mid += '|' + bb + '      ' + br
                else:
                    # Otherwise, make sure the object is an instance of Piece and concatenate the middle of the cell containing the name of the piece.
                    #assert isinstance(row[i], Piece), 'Item in board is not a subclass of Piece!!!'
                    if (row_n%2 == 0 and i%2 == 0) or (row_n%2 == 1 and i%2 == 1):
                        mid += '|' + bw + fb
                    else:
                        mid += '|' + bb + fw
                    mid += '  %s  ' % row[i] + fr + br                        
            # Once each item in a row has been iterated, concatenate the top mid and bottom strings to board_str
            if row_n%2 == 0:
                board_str += top_even
                board_str += mid + '| %i\n' % (8-row_n)
                board_str += bot_even
            else:
                board_str += top_odd
                board_str += mid + '| %i\n' % (8-row_n)
                board_str += bot_odd                
            row_n += 1
        # Concatenate the column labels at the end to board_str before returning it
        board_str += '   1      2      3      4      5      6      7      8   \n'
        return board_str
    
    def __repr__(self):
        """
        Overriding the base function repr() to customize its behavior for instances of class Board.
        This method constructs a string representation of the chessboard based on the pieces in it.
        This is the version that gets printed to file and thus does not include ANSI escape sequences.
        """
        # The string representing the top of each row
        top = '|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|‾‾‾‾‾‾|\n'
        # The string representing the bottom of each row
        bot = '|______|______|______|______|______|______|______|______|\n'
        # Initializing an empty string which will be returned as the final string
        board_str = ''
        # Initializing the row number to be included as part of the board string
        row_n = 0
        for row in self._mat:
            # Initializing the string representing the middle section of each row
            mid = ''
            for i in xrange(len(row)):
                # If there is no piece in the current position
                if row[i] is None:
                    # concatenate a string representing the middle an empty cell to the mid string.
                    mid += '|      '
                else:
                    # Otherwise, concatenate a string containing the occupying piece name.
                    mid += '|  %s  ' % row[i]                     
            # Once each item in a row has been iterated, concatenate the top mid and bottom strings to board_str
            board_str += top
            board_str += mid + '| %i\n' % (8-row_n)
            board_str += bot
            row_n += 1
        # Concatenate the column labels at the end to board_str before returning it
        board_str += '   1      2      3      4      5      6      7      8   \n'
        return board_str
    
    def _add_pieces(self, pieces):
        """
        A method to add pieces to the board. Only meant to be used by the constructor/initializer.
            Arguments:
                pieces -- a list of pieces (rook and kings) to put on the chess board.
            Returns:
                None
        """
        # Assert that the argument is a list
        assert isinstance(pieces, list), 'Pieces must be a list!'
        # Iterate over the list
        for p in pieces:
            # Parse out the x and y coordinates of the position
            f, r = p.position
            # Convert rank to zero-indexed row
            row = 8 - r
            # Convert file to zero-indexed column
            column = f - 1
            # Add the piece to the corresponding location in the array
            self._mat[row][column] = p
        
class GameState(object):
    """
    The instances of this class represent states of the chess game. This class is used
    as a superclass for GameState, which includes additional methods and attributes.
    Thus, instances of this class are primarily used for states that are considered during
    the process of searching the game tree.
    """
    
    """
    Overriding native Python methods for instances of this class
    """
    def __init__(self, KX, RX, KY, max_level, level=0, parent=None):
        """
        Constructor for the chessboard state node.
            Arguments:
                KX   -- Player X's king and its designated position.
                RX   -- Player X's rook and its designated position.
                KY   -- Player Y's king and its designated position.
                level  -- Int value to designate the level of the node (in reference to the original root node). Default is 0.
            Returns:
                None
        """
        # Type assertions
        assert isinstance(KX, King) and isinstance(RX, Rook) and isinstance(KY, King)
        assert KX.owner is RX.owner and KX.owner is not KY.owner
        assert type(level) is int
        
        # Set the piece position objects as attributes to the current state
        self.KX = KX
        self.RX = RX
        self.KY = KY
        
        # Setting the players
        self.player_x = KX.owner
        self.player_y = KY.owner
                
        # Initialize game variables
        self.level = level
        self.max_level = max_level
        self.legal_moves = self._get_legal_moves()
        self.game_status = self._get_game_status()
        self._children = []
        self.parent = parent
        
        # Make sure the game status is okay/not terminal
        if self.game_status in ['continue', 'check'] and self.max_level > self.level:
            self.is_leaf = False
        # If not, erase any legal moves and set it as a leaf
        else:
            self.legal_moves = []
            self.is_leaf = True
    
    def __str__(self):
        """
        String format for objects of class GameState.
        Outputs a string that consists of the current state's level and each piece's position.
        """
        return 'Level = %r. KX: %r, RX: %r, KY: %r' % (self.level, self.KX.position, self.RX.position, self.KY.position)
    
    def __repr__(self):
        """
        String representation for objects of class GameState.
        Outputs a string that consists of the string representation each piece.
        """        
        return repr(self.KX) + ' ' + repr(self.RX) + ' ' + repr(self.KY)
    
    def __getattr__(self, attr):
        """
        Overrides the base getattr() function, which gets called on an instance when the attribute
        in question cannot be found through the normal channels (__getattribute__ or __dict__).
        The purpose of this function is to allow memoization of lists that require lots of time when
        called many times.
        """
        # Compute x_attacking_positions and set the attribute
        if attr == 'x_attacking_positions':
            self.x_attacking_positions = self._positions_under_attack(self.player_x)
            return super(GameState, self).__getattribute__(attr)
        # Compute y_attacking_positions and set the attribute
        if attr == 'y_attacking_positions':
            self.y_attacking_positions = self._positions_under_attack(self.player_y)
            return super(GameState, self).__getattribute__(attr)        
    
    ### Comparison Operators ###
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.KX == other.KX and self.RX == other.RX and self.KY == other.KY
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    """ METHODS """        
    ## Instance Methods
    def check_cycle(self, min_length=2, max_length=6):
        """
        Checks to see if the current state is in a cycle, i.e. if the states have been repeating.
            Arguments:
                max_length -- the maximum length of a cycle to check. This number should be even since
                                there are 2 players, so cycles will have an even length.
            Returns:
                a boolean value indicating whether a cycle has been detected
        """
        # Must be even
        assert min_length % 2 == 0 and max_length % 2 == 0 and max_length > min_length
        # Early return if there is no parent
        if self.level < 4:
            return False
        # Create a deque containing the last threshold*6 ancestors
        p = self.parent
        d = deque()
        c = 0
        while p is not None and c < max_length*2:
            # Appending left so the newest ancestors are in the front
            d.appendleft(p)
            p = p.parent
            c += 1
            
        # If the length of ancestors is not long enough to really evaluate, return early with False
        if len(d) < min_length*2:
            return False
        
        # Create a list of lengths to try starting from min_length
        # to the size of the ancestor deque divided by threshold
        lengths = filter(lambda x: x%2 == 0, range(min_length, max_length))
        
        # Iterate over each legnth
        for l in lengths:
            if list(islice(d,0,l)) == list(islice(d,l,2*l)):
                return True
        return False
    
    def child_from_move(self, move):
        """
        Creates a child state from a given move, represented by a piece.
        Used for generating potential successor states and for generating states
        via user input.
            Arguments:
                move -- an instance of Rook or King with a new position.
            Returns:
                a child state with the new move
        """
        ## If the owner is player x, then it can be a rook or a king
        if move.owner is self.player_x:
            # If its a rook
            if isinstance(move, Rook):
                return GameState(self.KX, move, self.KY, self.max_level, level=self.level+1, parent=self)
            # Otherwise it must be a king
            else:
                return GameState(move, self.RX, self.KY, self.max_level, level=self.level+1, parent=self)
        # If not player x, then this must be player y's king
        else:
            return GameState(self.KX, self.RX, move, self.max_level, level=self.level+1, parent=self)
        
    def piece_under_attack(self, piece):
        """
        This method determines whether a piece is under attack.
        Returns true if the specified piece is under attack. Otherwise, returns false.
        
            Arguments:
                piece -- the piece to be checked whether its under attack or not.
            Returns:
                boolean value indicating whether the specified piece is under attack by checking the opponent's attacking positions.
        """
        # Type assertion
        assert isinstance(piece, King) or isinstance(piece, Rook)
        
        # Find opponent
        if piece.owner is self.player_x:
            opponent = self.player_y
        else:
            opponent = self.player_x
        
        # Return the boolean result of checking whether the position is in the list of positions under attack by the opponent.
        if opponent is self.player_x:
            KX_attacking, RX_attacking = zip(*self.x_attacking_positions)
            return piece.position in KX_attacking or piece.position in RX_attacking
        else:
            return piece.position in self.y_attacking_positions
    
    def rook_filter(self):
        """
        Creates an anonymous function for use as a filter for the rook's attacking positions
        based on the fact that spaces blocked by its own king are not under attack by that rook.
            Arguments:
                None (there is only one rook so this is unnecessary)
            Returns:
                rook_filter -- a lambda function to use as a filter for the rook's attacking positions,
                                or a None value which can also be used as a filter function.
        """
        # Default rook_filter to None
        rook_filter = None
        
        # If KX and RX are in the same column
        if self.KX.position.file == self.RX.position.file:
            # Filter out positions past KX
            if self.KX.position.rank > self.RX.position.rank:
                rook_filter = lambda position: self.KX.position.rank > position.rank
            else:
                rook_filter = lambda position: self.KX.position.rank < position.rank
        # If KX and RX are in the same row
        elif self.KX.position.rank == self.RX.position.rank:
            # Filter out positions past KX
            if self.KX.position.file > self.RX.position.file:
                rook_filter = lambda position: self.KX.position.file > position.file
            else:
                rook_filter = lambda position: self.KX.position.file < position.file
        return rook_filter
    
    def king_filter(self, king):
        """
        Creates an anonymous function for use as a filter for the king's attacking positions
        based on the fact that the king is not permitted to move to a checked/"attacked" position.
            Arguments:
                king -- the king in question to create the filter for. the key difference is whether the
                        king belongs to player X or Y.
            Returns:
                king_filter -- a lambda function to sue as a filter function for the king's attacking positions,
                                or a None value with can also be used as a filter function.
        """
        # Assert argument is a king
        assert isinstance(king, King)
        
        # Default filter to None
        king_filter = None
        
        # If this is KX and it's X's turn
        if king.owner is self.player_x and self.current_player is self.player_x:
            # Set the filter to exclude positions that would put the king in check
            KX_attacking, _ = zip(*self.x_attacking_positions)
            checked_attacking_positions = list(set(KX_attacking) & set(self.y_attacking_positions))
            checked_attacking_positions.append(self.RX.position)
            king_filter = lambda position: position not in checked_attacking_positions
        # If this is KY and it's Y's turn
        elif king.owner is self.player_y and self.current_player is self.player_y:
            # Set the filter to exclude positions that would put the king in checkf
            KX_attacking, RX_attacking = zip(*self.x_attacking_positions)
            checked_attacking_positions = list((set(KX_attacking) & set(self.y_attacking_positions)) | (set(RX_attacking) & set(self.y_attacking_positions)))
            king_filter = lambda position: position not in checked_attacking_positions
        return king_filter
    
    def cleanup(self, successor):
        """
        Deletes unnecessary data that is not collected by garbage collection due to referencing.
        Should only be called upon once the game has already passed this state.
            Arguments:
                successor -- the chosen child for the next state
            Returns:
                None
        """
        # Remove old data about attacking positions and legal moves
        del self.x_attacking_positions
        del self.y_attacking_positions
        del self.legal_moves
        if successor.KX != self.KX:
            del self.KX.attacking_positions
        if successor.RX != self.RX:
            del self.RX.attacking_positions
        if successor.KY != self.KY:
            del self.KY.attacking_positions
        # Remove old children list
        del self._children
        
    def print_board(self, before=None):
        """
        Prints the string representation of the current instance to the standard output and the file gameResults.txt.
            Arguments:
                before -- a string to concatenate to the beginning of the board string. This is used to add
                            a message saying that the game is starting and mentioning if it is a test case or not.
                            This ensures that the description gets printed to the gameResults.txt file as well.
            Returns:
                None
        """
        ## Set up the board representation
        self.board = Board([self.KX, self.RX, self.KY])
        ## Setting up separate strings to print on screen and to file
        game_str = ''
        
        # Check to see if a string was given to print at the top
        if before is not None:
            assert type(before) is str
            game_str += before
        
        # Add a border on top if the level is even, means it is the start of a new set of turns
        if self.level % 2 == 0:
            game_str += '-----------------------------------------------------------------\n\n'
        
        ## Add information about the current status of the game
        # Calculate and display the number of turns completed
        turns = self.level/2
        # Display which player's turn it is only if the game status indicates the game is ongoing
        if self.game_status in ['continue', 'check']:
            game_str += 'Number of turns completed: %i\n' % turns
            game_str += "It is currently %s's turn.\n" % self.current_player
            
        # Display if a player (should only be player Y) is in check
        if self.game_status == 'check':
            game_str += "%s is in check!\n" % self.current_player
        
        # Display certain information if the game is over (determined by whether the state is a leaf)
        if self.is_leaf:
            # Display if the game is in checkmate
            if self.game_status == 'checkmate':
                game_str += 'Checkmate! Player X wins!\n'
            # If the game is a leaf and is not checkmate, it has come to a draw for one of several possible reasons.
            # This will display the reason given based on the game_status attribute.
            else:
                game_str += 'Game has reached a draw due to: %s\n' % self.game_status
            game_str += 'A total of %i moves were made out of %i.\n' % (turns, self.max_level/2)
            game_str += 'Game over!\n'
        # Adding an extra new line for nicer formatting
        game_str += '\n'
        # Create a separate string to print to screen and to gameResults.txt (to get rid of ANSI escape codes in the text file)
        board_str_print = game_str + str(self.board)
        board_str_file = game_str + repr(self.board)

        # Print the string onto the screen
        print board_str_print
        
        # Append the other string to the end of the gameResult.txt file
        game_result_file = open('gameResult.txt', 'a')
        game_result_file.write(board_str_file)
        game_result_file.close()
    
    ## Private Methods
    def _positions_under_attack(self, player):
        """
        This method determines generates a list of positions that are under attack by the pieces of the specified player.
        It is a private method as it is intended to be called for setting the attributes x_attacking_positions and y_attacking_positions.
            Arguments:
                player -- the attacking player. The returned list contains positions under attack by this player's piece(s)
            Returns:
                for player X, a list of tuples containing king and rook attacking position, respectively (self.x_attacking_positions)
                for player Y, a list containing the king's attacking positions (self.y_attacking_positions)
        """
        assert player is self.player_x or player is self.player_y, 'Must be a player in the current state!'
        if player is self.player_x:
            rook_filter = self.rook_filter()
            return GameUtils.zip_longest(self.KX.attacking_positions, filter(rook_filter, self.RX.attacking_positions))
        else:
            return self.KY.attacking_positions
 
    def _get_legal_moves(self):
        """
        Returns all legal moves for the current state based on whose turn it is (the current_player property).
            Arguments:
                None
            Returns:
                list of legal moves represented as pieces
        """
        moves = []
        # If it is player X's turn
        if self.current_player is self.player_x:
            # Iterate through X's attacking positions
            king_filter = self.king_filter(self.KX)
            for KX_position, RX_position in self.x_attacking_positions:
                # Add them if they are not in Y's attacking positions
                if KX_position is not None and KX_position not in self.y_attacking_positions and king_filter(KX_position):
                    moves.append(self.KX.move(KX_position))
                if RX_position is not None and RX_position not in self.y_attacking_positions:
                    moves.append(self.RX.move(RX_position))
            return moves
        # If its player Y's turn
        else:
            # Set up the king filter
            king_filter = self.king_filter(self.KY)
            KY_attacking = filter(king_filter, self.y_attacking_positions)
            # Iterate through KY attacking positions and add them if they are not in X's attacking positions.
            for KY_position in KY_attacking:
                if KY_position not in self.x_attacking_positions:
                    moves.append(self.KY.move(KY_position))
            return moves
        
    def _get_game_status(self):
        """
        Computes the game_status attribute. The class constructor calls this function to set the attribute upon initialization.
            Arguments:
                None
            Returns:
                the game status
        """
        # Sanity check to make sure no piece shares a position (for user input and test case purposes)
        if self.KX.position == self.RX.position or self.KY.position == self.RX.position or self.KX.position == self.KY.position:
            return 'illegal'
        
        # If there are no legal moves for this turn,
        if not self.legal_moves:
            # and if it is player Y's turn and player Y's king is under attack,
            if self.current_player is self.player_y:
                if self.piece_under_attack(self.KY):
                    # the status returns as checkmate.
                    return 'checkmate'
                # If player y's king is NOT under attack but player y has no legal moves left, then it is a stalemate.
                else:
                    return 'stalemate'
            # This return shouldn't happen, but will occur if it is player x's turns but there are no legal moves left.
            else:
                return 'no moves left'
        else:
            # If there are still legal moves then check to see if any could end the game.
            if self.current_player is self.player_y:
                if self.piece_under_attack(self.RX):
                    return 'insufficient materials'
                if self.piece_under_attack(self.KX):
                    return 'illegal'
                if self.piece_under_attack(self.KY):
                    return 'check'
            else:
                if self.piece_under_attack(self.KY):
                    return 'illegal'
        if self.level >= self.max_level:
            return 'maximum turns reached'
        return 'continue'
    
    """ PROPERTIES """
    @property
    def current_player(self):
        """
        Returns an object referencing the player whose turn it is in the current state.
        """
        if self.level % 2 == 0:
            return self.player_x
        else:
            return self.player_y
    
    @property    
    def children(self):
        """
        Generator for child states, returning them one by one instead of a whole list.
        """
        # Checks to see if the private attribute has been set yet, if so it yields each item in it
        # Note: private attribute self._children is different than self.children: the private attribute
        # is a list of tuple pairs containing the move made to get to the child and the child state itself.
        if self._children:
            for _, child in self._children:
                yield child
                
        # If the private attribute is the same length as legal moves, then return from the property
        if len(self._children) == len(self.legal_moves):
            return
        
        # Otherwise, iterate through legal moves, yielding ones not found in the private attribute and adding them afterwards.
        for move in self.legal_moves:
            if move not in [c[0] for c in self._children]:
                child = self.child_from_move(move)
                yield child
                self._children.append((move, child))