"""
game.py - The file that is imported
Copyright 2016, David Jarrett (wuufu.co.uk)

Locations are imported directly into the story. This way, the can be called
by story elements as and when they need to be, and there is a single point
of entry from app.py's perspective.
"""

from game.locations import home


def load(gstory):
    gstory.add_location("home", home.Home)
