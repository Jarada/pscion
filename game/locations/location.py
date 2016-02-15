"""
location.py - The central location class, all inherit
Copyright 2016, David Jarrett (wuufu.co.uk)

This contains the core class for managing the location elements within the game.
All necessary imports are linked here.
"""

from game.commands.command import SendMessage, UpdateLocationName


class Location:

    ACT_LOOK = {"value": "l-look", "icon": "eye", "text": "Look", "optgroup": "area", "optlabel": "Area"}
    ACT_EXAMINE = {"value": "l-examine", "icon": "search", "text": "", "optgroup": "examine", "optlabel": "Examine"}
    ACT_PICKUP = {"value": "l-pickup", "icon": "hand-grab-o", "text": "", "optgroup": "pickup", "optlabel": "Pickup"}

    def __init__(self, key, name, pronoun=""):
        self.key = key
        self.name = name
        self.pronoun = pronoun
        self.linked = []

    def actions(self, player):
        pass

    def look(self, player):
        pass

    def examine(self, player, item):
        pass

    def pickup(self, player, item):
        pass

    def travel(self, player):
        pass

    def _update_location(self, msg, time=1000):
        return [
            UpdateLocationName(self.name),
            SendMessage("", msg, time)
        ]

    def travel_str(self, prev):
        msg = "You move into"
        if self.pronoun:
            msg += " %s" % self.pronoun
        msg += " %s." % self.name
        return self._update_location(msg)

    @staticmethod
    def _act_examine(key, name):
        act_examine = Location.ACT_EXAMINE.copy()
        act_examine["value"] = "%s-%s" % (act_examine["value"], key)
        act_examine["text"] = name
        return act_examine

    @staticmethod
    def _act_pickup(key, name):
        act_pickup = Location.ACT_PICKUP.copy()
        act_pickup["value"] = "%s-%s" % (act_pickup["value"], key)
        act_pickup["text"] = name
        return act_pickup
