"""
damage.py - Manages the damage
Copyright 2016, David Jarrett (wuufu.co.uk)

Damage comes in multiple flavours. This class is designed to deal with the multiple varieties.
"""


class Damage:
    def __init__(self, dealt=0):
        self.damage = []
        if dealt > 0:
            self.add(dealt)

    def add(self, dmg):
        self.damage.append(dmg)

    def get(self, index):
        if len(self.damage) > index:
            return self.damage[index]
        return 0

    def total(self):
        tdmg = 0
        for dmg in self.damage:
            tdmg += int(dmg)
        return tdmg
