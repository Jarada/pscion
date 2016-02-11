"""
location.py - The central location class, all inherit
Copyright 2016, David Jarrett (wuufu.co.uk)

This contains the core class for managing the location elements within the game.
All necessary imports are linked here.
"""


class Location:

    ACT_LOOK = {"value": "l-look", "icon": "eye", "text": "Look", "optgroup": "area", "optlabel": "Area"}
    ACT_EXAMINE = {"value": "l-examine", "icon": "search", "text": "", "optgroup": "examine", "optlabel": "Examine"}
    ACT_PICKUP = {"value": "l-pickup", "icon": "hand-grab-o", "text": "", "optgroup": "pickup", "optlabel": "Pickup"}

    def __init__(self, key, name):
        self.key = key
        self.name = name

    def actions(self, player):
        raise NotImplementedError

    def look(self, player):
        raise NotImplementedError

    def examine(self, player, item):
        raise NotImplementedError

    def pickup(self, player, item):
        raise NotImplementedError

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
