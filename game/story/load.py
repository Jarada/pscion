"""
game.py - The file that is imported
Copyright 2016, David Jarrett (wuufu.co.uk)

This is the file the app.py imports. It sets up the story and the elements, and prepares the
game for the level needed.
"""

from game.story import tutorial


def load(gstory):
    tutorial.load(gstory)
