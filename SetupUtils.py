#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SetupUtils.py

This module contains global functions used in the setup/menu portion of the program.
"""

### Python Library imports
from re import split

import GameClasses
import GameUtils
#from pympler.tracker import SummaryTracker
#tracker = SummaryTracker()


""" Setup Functions """
query_until = GameUtils.query_until
query_until_parsed = GameUtils.query_until_parsed

def begin_setup():
    """
    A function to ask two initial questions to the current user: if this is a test mode and what is the maximum number of moves.
        Arguments:
            None
        Returns:
            test_mode -- a Boolean value indicating whether the game will be played in test mode or not.
            n -- the specified maximum number of moves. Default value is 35.
    """
    # Ask if this is a test
    yes_no_condition = lambda response: response.upper() in ['Y','YES','N','NO']
    test_mode_str = query_until('Is this a test? (Y/N)', yes_no_condition)    
    # If it is a test, set testMode to True.
    if test_mode_str.upper() in ['Y', 'YES']:
        test_mode = True
    # Otherwise, set it to false.
    else:
        test_mode = False
        
    # Ask for the n value (maximum number of moves)
    n_condition = lambda n: (n.isdigit() and n != '0')
    n_str = query_until('Please enter the maximum number of moves [default: 35]', n_condition, default='35')
    n = int(n_str)
    
    return (test_mode, n)

def test_mode_setup(n):
    """
    A function to set up test mode. It reads from the testCase.txt file to get a test case from each line.
    It calls on parse_test_case to ensure the line is properly formatted and create the necessary objects to start playing.
        Arguments:
            n -- the maximum number of moves.
        Returns:
            None
    """
    # Read the test case file and break up new lines as separate strings
    test_case_file = open('testCase.txt')
    test_cases = []
    for line in test_case_file:
        if line != '\n' and line[0] != '#':
            test_cases.append(line.strip())
    test_case_file.close()
    
    # Initialize players
    player_x = GameClasses.Player('X')
    player_y = GameClasses.Player('Y')
    #tracker.print_diff()
    # Parse and run each test case
    for case in test_cases:
        if parse_test_case(case, player_x, player_y) is not None:
            test_case_name, KX, RX, KY = parse_test_case(case, player_x, player_y)
        else:
            print 'There was an error parsing the following test case: %s. Skipping to the next case.' % case
            continue
        root_state = GameClasses.GameState(KX, RX, KY, n*2)
        if root_state.game_status != 'continue':
            print 'Test case "%s" root state is not a legitimate starting state (status: %s). Skipping to the next case if there is one.' % (test_case_name, root_state.game_status)
            continue
        GameUtils.play(root_state, test_mode=True, case_name=test_case_name)
        #tracker.print_diff()
        
def competition_setup(n):
    """
    A function to set up competition mode. It reads gathers user input for each piece and checks/parses the information using parse_position
    to initialize the GameClasses.Position tuples for each piece. The function then uses these initialized objects to start playing the game.
        Arguments:
            n -- the maximum number of moves.
        Returns:
            None
    """
    name_condition = lambda name: name.upper() in ['X','Y']
    ai_player = query_until('Which player should I play as? (X/Y)', name_condition)    
    if ai_player == 'X':
        player_x = GameClasses.Player('X')
        player_y = GameClasses.Player('Y', input_mode=True)
    else:
        player_x = GameClasses.Player('X', input_mode=True)
        player_y = GameClasses.Player('Y')        
    
    status_confirmed = False
    while not status_confirmed:
        print 'Please enter ordered pairs of row and column numbers for the following pieces (e.g., (1,2) is row 1, column 2):'
        KX_position = query_until_parsed("Player X's king:", parse_position)
        KX = GameClasses.King(player_x, KX_position)
        RX_condition = lambda position: position != KX_position
        RX_position = query_until_parsed("Player X's rook:", parse_position, condition=RX_condition)
        RX = GameClasses.Rook(player_x, RX_position)
        KY_condition = lambda position: position != KX_position and position != RX_position
        KY_position = query_until_parsed("Player Y's king:", parse_position, condition=KY_condition)     
        KY = GameClasses.King(player_y, KY_position)
        
        root_state = GameClasses.GameState(KX, RX, KY, n*2)
        if root_state.game_status == 'continue':
            status_confirmed = True
        else:
            print 'The initial state returned with a status of "%s". Please try again.' % root_state.game_status
    GameUtils.play(root_state, test_mode=False)

""" Parsing Functions """
def check_coordinates(file_str, rank_str):
    """
    This function checks the coordinates given by user input and test case input
    and is called by a parsing function. Although it does not directly raise exceptions
    when invalid values are passed in, it returns a None value, which is handled by the calling parsing function.
    
        Arguments:
            file_str -- a string from the parsing function representing the file (column).
                        Note: a valid file_str can be represented as either the standard algebraic notation
                        letter or as an integer representing the same value (e.g., a = 1, b = 2, etc.)
            rank_str -- a string from the parsing function representing the rank (row)
        Returns:
            A (f, r) tuple where f (file) and r (rank) are integers, or None if input was invalid.
    """
    file_error = ValueError('The file must be an integer (1-8) or a letter (a-g). Please try again.')
    rank_error = ValueError('The rank must be an integer (1-8). Please try again.')
    ## Process the file input
    try:
        if len(file_str) != 1:
            raise file_error
        if file_str.isalpha() and ord(file_str.lower()) in range(ord('a'),ord('g')+1):
            # This maps lower case characters to their corresponding numeric values
            f = ord(file_str.lower()) - 96
        else:
            f = int(file_str)
        if f < 1 or f > 8:
            raise file_error
    except ValueError as E:
        print type(E), E
        return None
    ## Process the column input
    try:
        if len(rank_str) != 1 or not rank_str.isdigit():
            raise rank_error
        r = int(rank_str)
    except ValueError as E:
        print type(E), E
        return None
    return (f, r)

def parse_test_case(tc, player_x, player_y):
    """
    Parses a line (specified as the argument tc) from the test case file.
    Returns the three game pieces that each test case gives info about.
        Arguments:
            tc -- a line from the test case file.
            player_x -- an instance of Player representing player x
            player_y -- an instance of Player representing player y
        Returns:
            test_case_name -- a string containing the name of the test case as interpted from the current line.
            KX -- an instance of PieceGameClasses.Position representing player x's king and its position indicated in the test case line.
            RX -- an instance of PieceGameClasses.Position representing player x's rook and its position indicated in the test case line.
            KY -- an instance of PieceGameClasses.Position representing player y's king and its position indicated in the test case line.
    """    
    strs = split(' ', tc)
    for s in strs[1:]:
        if len(s) != 8:
            print 'Incorrect syntax for input: %s. Example of correct syntax: x.K(2,4)' % s
            return None
        if check_coordinates(s[4],s[6]) is None:
            return None
        f, r = check_coordinates(s[4],s[6])
        if s[0].upper() == 'X':
            if s[2].upper() == 'R':
                RX = GameClasses.Rook(player_x, GameClasses.Position(f, r))
            elif s[2].upper() == 'K':
                KX = GameClasses.King(player_x, GameClasses.Position(f, r))
            else:
                print 'Player X can only be assigned a king or rook. Error came from the following test case: %s' % strs
                return None
        elif s[0].upper() == 'Y':
            if s[2].upper() == 'K':
                KY = GameClasses.King(player_y, GameClasses.Position(f, r))
            else:
                print 'Player Y can only be assigned a king. Error came from the following test case: %s' % strs
                return None
        else:
             print 'Error reading this testcase: %s' % strs
             return None
    test_case_name = strs[0][:-1]
    return (test_case_name, KX, RX, KY)

def parse_position(op):
    """
    Parses an ordered pair string from user input. Used for setting initial locations of the pieces in competition mode.
        Arguments:
            op -- a string containing an ordered pair in the format of (x,y) where x is the row and y is the column.
        Returns:
            an instance of GameClasses.Position containing the specified x and y coordinates.
    """
    strs = split('[\.(,)]', op)
    strs = filter(None, strs)
    if len(strs) == 2:
        if check_coordinates(strs[0], strs[1]) is not None:
            f, r = check_coordinates(strs[0], strs[1])
            return GameClasses.Position(f, r)
    else:
        return None
