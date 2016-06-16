#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main.py

This module contains the main execution of the game.

Written by: Sam Handelman
CPSC 481 - Artificial Intelligence
Assignment 1 - KRK Chess Endgame with Mini-Max
"""
# Imports
import SetupUtils

def main():
    # Initial setup to gather test_mode and n
    test_mode, n = SetupUtils.begin_setup()
    
    # Set up for test mode
    if test_mode:
        SetupUtils.test_mode_setup(n)
    # Set up for competition mode
    else:
        SetupUtils.competition_setup(n)

    restart_str = raw_input('Would you like to play again? (y/n) >> ').upper()
    while restart_str not in ['Y','YES','N','NO']:
        print '%s is not a valid response.' % restart_str
        restart_str = raw_input('Would you like to play again? (y/n) >> ').upper()
    
    if restart_str in ['Y','YES']:
        main()
    else:
        exit(0)

if __name__ == '__main__':
    """
    This is the script that is run upon executing the file. It goes through the setup functions,
    which subsequently call the play function to start the game.
    """
    
    # Print opening banner
    print '*******************************************'
    print '*** Assignment 1: Mini-Max KRK End Game ***'
    print '*******************************************\n'

    # Run main function for the program
    main()
