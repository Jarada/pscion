"""
story.py - The central story class, all inherit
Copyright 2016, David Jarrett (wuufu.co.uk)

Home Sweet Home
"""

from game.locations import location
from game.commands.command import SendMessage, UpdateLocationActions


class Home(location.Location):
    def __init__(self):
        super().__init__("home", "Home")

    def actions(self, player):
        if player.gamemajor == 0 and player.gameminor == 0 and player.gamestate == 1:
            return [location.Location.ACT_LOOK]
        elif player.gamemajor == 0 and player.gameminor == 0 and player.gamestate > 1:
            return [location.Location.ACT_LOOK,
                    self._act_examine("book", "Book"),
                    self._act_examine("chip", "Credit chip"),
                    self._act_examine("lamp", "Lamp"),
                    self._act_examine("sofa", "Sofa")]

    def examine(self, player, item):
        pass

    def pickup(self, player, item):
        pass

    def look(self, player):
        return [SendMessage("", "The room is sparsely decorated. You have your bed in the corner, with a bedside "
                                "cabinet upon which a lamp is placed. There is a sofa just next to this with a book "
                                "laid on it, and a TV on the far wall. Two doors either side of the TV lead to the "
                                "kitchen and bathroom respectively, and a door to the left leads to the exit. There is "
                                "a Credit chip on the floor.", 8000)]
