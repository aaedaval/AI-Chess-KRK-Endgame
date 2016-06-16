#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GameUtils.py

This module contains global functions and variables used in the game.
"""

import GameClasses


### Play Function ###
def play(root_state, test_mode, case_name=None):
    """
    The driving function for playing the KRK endgame.
        Arguments:
            root_state -- the root state of the current game that is about to start. It contains n, the maximum number of moves.
            test_mode -- a Boolean value indicating whether to play in test mode or not. If false, that indicates that this is competition mode.
            case_name -- a string containing the name of the test case as read from the test case file. Default value is set to None.
        Returns:
            None
    """
    
    # Set up local objects referencing the players
    player_x = root_state.player_x
    player_y = root_state.player_y
        
    if test_mode:
        assert case_name is not None and type(case_name) is str, 'Need to have a valid test case name for test mode!'
    else:
        assert case_name is None, 'There should be no case name if this is not test mode!'
    # Create the initial game state
    start_str = '\n\n-----------------------------------------------------------------\n'
    if test_mode:
        start_str += '*** TEST MODE ***\nImplementing %s\n' % case_name
    start_str += 'Starting game...\n'
    current_state = root_state
    status = current_state.game_status
    current_state.print_board(before=start_str)
    # Iterate the game play until either the maximum number of moves have been made or stalemate/checkmate is returned
    while not current_state.is_leaf:
        # Player X makes a move
        current_state = player_x.move(current_state)
        # Check if the game is over
        if current_state is None:
            return
        current_state.print_board()
        # Player Y makes a move
        current_state = player_y.move(current_state)
        # Check if the game is over
        if current_state is None:
            return
        current_state.print_board()
        
    
### Distance Functions ###
## Center Manhattan Distance lookup table
CMD = [
    [6, 5, 4, 3, 3, 4, 5, 6],
    [5, 4, 3, 2, 2, 3, 4, 5],
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 2, 1, 0, 0, 1, 2, 3],
    [3, 2, 1, 0, 0, 1, 2, 3],
    [4, 3, 2, 1, 1, 2, 3, 4],
    [5, 4, 3, 2, 2, 3, 4, 5],
    [6, 5, 4, 3, 3, 4, 5, 6]
]

def cent_man_dist(position):
    """
    Returns the center Manhattan distance of a given piece, which is the Manhattan distance to the nearest of the 4 centered positions.
        Arguments:
            position -- an instance of position
        Returns:
            the center Manhattan distance
    """
    # Parse out the rank and file coordinates of the position
    f, r = position
    # Return the answer by looking up from the table
    row = 8-r
    column = f-1
    return CMD[row][column]

def man_dist(pos1, pos2):
    """
    Returns the Manhattan distance of two positions.
        Arguments:
            pos1 -- an instance of Position.
            pos2 -- an instance of Position.
        Returns:
            Manhattan distance, which is the sum of the x and y distances between the two positions
    """
    # Compute the file distance
    df = abs(pos1.file - pos2.file)
    # Compute the rank distance
    dr = abs(pos1.rank - pos2.rank)
    # Return their sum
    return df + dr

def chesbyshev_distance(pos1, pos2):
    """
    Returns the Chesbyshev distance of two positions.
        Arguments:
            pos1 -- an instance of Position.
            pos2 -- an instance of Position.
        Returns:
            Chesbyshev distance (the max of the x and y distances)
    """
    # Compute x distance
    df = abs(pos1.file - pos2.file)
    # Compute y distance
    dr = abs(pos1.rank - pos2.rank)
    # Return the max of the two distances
    return max(df, dr)

### Miscellaneous Functions ###
def query_until(prompt, condition, default=None):
    """
    Query a prompt to the user until the response satisfies the given condition.
        Arguments:
            prompt -- a string containing the prompt to ask
            condition -- a function (lambda works) that returns True if the response meets the desired condition
                            but returns False otherwise.
            default -- the default value for the response; only returned if input is empty. Default is None.
        Returns:
            response -- the string containing the user's response
    """
    assert type(prompt) is str and callable(condition)
    response = raw_input(prompt + ' >> ')
    if default is not None and not response:
        return default
    while not condition(response):
        if default is not None and not response:
            return default
        print "'%s' is not a valid response." % response
        response = raw_input(prompt + ' >> ')
    return response

def query_until_parsed(prompt, parse_func, condition=None):
    """
    Query a prompt to the user until it can be successfully parsed.
        Arguments:
            prompt -- a string containing the prompt to ask
            parse_func -- a function that takes just the response as an argument then
                          parses and returns the desired object, or returns None if the
                          input is invalid.
            condition -- a lambda function to determine if the input meets certain criteria.
                        Default is set to None; this argument is optional.
        Returns
            parsed_object -- the object returned successfully by parse_func
    """
    assert type(prompt) is str and callable(parse_func)
    response = raw_input(prompt + ' >> ')
    parsed_object = parse_func(response)
    while parsed_object is None:
        print "Could not parse '%s' Please check your syntax." % response
        response = raw_input(prompt + ' >> ')
        parsed_object = parse_func(response)
    if condition is not None:
        while not condition(parsed_object) or parsed_object is None:
            print "'%s' is not a valid response." % response
            response = raw_input(prompt + ' >> ')
            parsed_object = parse_func(response)
    return parsed_object

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
    ## Error for when the file entered is invalid
    file_error = ValueError('The file must be an integer (1-8) or a letter (a-g). Please try again.')
    ## Error for when the rank entered is invalid
    rank_error = ValueError('The rank must be an integer (1-8). Please try again.')
    try:
        ## Process the file input
        # The string should have a length of 1, i.e. it should be a character
        if len(file_str) != 1:
            raise file_error
        # If the string contains letters
        if file_str.isalpha():
            # Make sure it is a letter between 'a' and 'g'
            if ord(file_str.lower()) in range(ord('a'),ord('g')+1):
                # This maps lower case characters to their corresponding numeric values
                f = ord(file_str.lower()) - 96
            # Otherwise, raise an exception
            else:
                raise file_error
        else:
            f = int(file_str)
        if f < 1 or f > 8:
            raise file_error
        
        ## Process the rank input
        # The string should have a length of 1, i.e. it should be a character
        # and it should be a digit
        if len(rank_str) != 1 or not rank_str.isdigit():
            raise rank_error
        # Convert the string into an int
        r = int(rank_str)
    # ValueError exception returns None when file_error or rank_error is raised
    except ValueError as E:
        print type(E), E
        return None
    return (f, r)

def zip_longest(list1, list2):
    """
    Zip together two lists into a list of tuples. Unlike builtin zip, it goes until the longest list, adding None for missing values of the shorter list.
        Arguments:
            list1 - a list
            list2 - another list
        Returns:
            a list of tuples with the values from list1 and list2
    """
    zipped = zip(list1, list2)
    if len(list1) < len(list2):
        zipped += [(None, item) for item in list2[len(list1):]]
    elif len(list1) > len(list2):
        zipped += [(item, None) for item in list1[len(list2):]]
    return zipped