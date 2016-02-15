"""
corridor.py - The corridor outside your home
Copyright 2016, David Jarrett (wuufu.co.uk)

Like your home, this is one of the few areas that is described with such a simple noun.
"""

from game.locations import location
from game.commands.command import SendMessage, UpdateLocationActions
from game.model.item import Item


class Corridor(location.Location):
    def __init__(self):
        super().__init__("corridor", "Corridor", "the")

    def actions(self, player):
        return [location.Location.ACT_LOOK]

    def look(self, player):
        return [SendMessage("", "The corridor outside your home is pretty sparse. It bends round here and bends round "
                                "there and there aren't many people out and about.", 6000)]

    def travel(self, player):
        if player.later_eq(0, 0, 3):
            return ['home']

    def travel_str(self, prev):
        if prev == 'home':
            return self._update_location('You open your front door and move out into %s %s.'
                                         % (self.pronoun, self.name), 1500)
