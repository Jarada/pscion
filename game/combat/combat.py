"""
combat.py - Deals with combat
Copyright 2016, David Jarrett (wuufu.co.uk)

Combat works in turns. The person to go first depends on the story and how the enemies were found. On the enemies
turns, they all choose an action based upon their energy levels, health and from the list of attacks available to
them.
"""

import math, random
from game.commands.command import CombatMessage


class Combat:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.turn = 'e' if enemies.first else 'p'

    def start(self):
        if self.turn == 'e':
            return self.enemies.actions(self.player)
        else:
            return [CombatMessage("You take the initiative!")]

    def turn(self, args):
        print(args)


class Enemies:
    def __init__(self, enemies, first=False):
        self.enemies = enemies
        self.first = first

    def actions(self, player):
        """
        :return: The result of the enemies acting
        """
        actions = []
        for enemy in self.enemies:
            actions.append(CombatMessage(enemy.action(player)))
        return actions


class Enemy:
    def __init__(self, player, name, health, energy, attacks):
        self.player = player
        self.name = name
        self.health = health
        self.energy = energy
        self.attacks = attacks

    def rest(self):
        return "%s is resting." % self.name

    def action(self, player):
        """
        :return: The results of the enemy acting
        """
        pass


class EnemyAttack:
    def __init__(self, name, actdes, target, energy, action, time=0):
        self.name = name
        self.actdes = actdes
        self.target = target  # Either f for friendly, p for player, c for companion or a for party
        self.energy = energy
        self.action = action
        self.time = time

    def _unpack(self):
        """
        :return: An unpacked dictionary of the skill

         The skill stores data in the database related to what the skill does including the target and the skills
         actions. This is stored in a single string. This function unpacks that string and turns it into a
         dictionary that is returned.
        """
        actsplit = str(self.action).split(";")
        print(actsplit)
        actdict = {}
        for keyvalue in actsplit:
            keyvaluesplit = keyvalue.split(":")
            actdict[keyvaluesplit[0]] = keyvaluesplit[1]
        return actdict

    def damage(self, enemy, adict=None):
        """
        :param player: The enemy who is using the skill
        :param adict: The unpacked dictionary to prevent unnecessary unpacking
        :return: The damage range done
        """
        adict = self._unpack() if not adict else adict
        player = enemy.player
        if 'd' in adict:
            d = float(adict['d'])
            if 'di' in adict and player.charlevel > 1:
                l = player.charlevel - 1
                d = math.floor(d + (l * float(adict['di'])))
            if 'dd' in adict:
                db = d - float(adict['dd'])
                dt = d + float(adict['dd'])
                return "%d|%d" % (int(db), int(dt))
            else:
                return "%d" % int(d)
        return "%d" % 0

    def total_energy(self, player, adict=None):
        """
        :param player: The player who is using the skill
        :param adict: The unpacked dictionary to prevent unnecessary unpacking
        :return: The total energy usage of the skill
        """
        adict = self._unpack() if not adict else adict
        if 'ei' in adict:
            l = player.charlevel - 1
            return math.floor(float(self.energy) + (l * float(adict['ei'])))
        return self.energy

    def precast(self):
        """
        :return: A result indicating how many turns you gotta wait
        """
        return self.time

    def cast_damage(self, caster, adict):
        """
        :param caster: The object representing the caster of the skill
        :param adict: The unpacked dictionary to prevent unnecessary unpacking
        :return: The number of damage done randomly chosen with available guidelines
        """
        dmg = self.damage(caster, adict)
        dmsplit = dmg.split("|")
        if len(dmsplit) == 2:
            return random.randint(int(dmsplit[0]), int(dmsplit[1]))
        else:
            return int(dmsplit[0])

    def cast(self, caster, target):
        """
        :param caster: The object representing the caster of the skill
        :param target: The object representing the target of the skill
        :return: A string representing the action that has occurred

         This does the EnemyAttack on the specified target as cast by the caster
        """
        adict = self._unpack()
        dealt = self.cast_damage(caster, adict)
        caster.energy -= self.total_energy(caster, adict)
        target.health -= dealt
        # TODO ADD SPAN CLASSES FOR STYLING
        des = self.actdes.replace('[s]', self.name)
        des = des.replace('[t]', target.name)
        des = des.replace('[d]', str(dealt))
        return des
