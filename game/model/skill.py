#!/usr/bin/env python
# coding=utf-8
"""
skill.py - Skill database model
Copyright 2016, David Jarrett (wuufu.co.uk)

Each character class has eight skills; four primary and four secondary. Primary skills can only be used by someone who
wields the primary class with those skills, while secondary skills can be used by anyone with a primary or secondary
class in that skill. This means that a dual classed player can have access to twelve skills to pick from, alongside
the standard skills (attack and resurrect).

This provides ample skills to customise your crew's four skill slots and set a play style that matches how you want to
fight.
"""

import math, random
from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, cclass


class Skill(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    cclass = ForeignKeyField(cclass.CharacterClass, related_name="skills", null=True)
    primary = BooleanField(default=True)
    name = TextField()
    image = CharField()
    description = TextField()
    energy = IntegerField()
    time = IntegerField()
    recharge = IntegerField()
    action = TextField()
    actiondescription = TextField()
    precastdescription = TextField(null=True)

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

    def _encode_str(self, player, des, target=None, dealt=0):
        adict = self._unpack()
        des.replace('[s]', '<span class="skill-sender">%s</span>' % player.name)
        if target:
            des = des.replace('[t]', '<span class="skill-target">%s</span>' % target.name)
            des = des.replace('[d]', '<span class="skill-dealt">%d</span>' % dealt)
        elif 'd' in adict:
            dmg = self.damage(player, adict)
            dmsplit = dmg.split("|")
            if len(dmsplit) == 2:
                des = des.replace('[d]', '<span class="skill-dmg">%d..%d</span>' %
                                  (int(dmsplit[0]), int(dmsplit[1])))
            else:
                des = des.replace('[d]', '<span class="skill-dmg">%d</span>' % int(dmsplit[0]))
        if 'cn' in adict:
            des = des.replace('[cn]', '<span class="skill-cn">%d</span>' % int(adict['cn']))
        return des

    def description_str(self, player):
        """
        :param player: The player who is using the skill
        :return: The description string with the relevant data included
        """
        des = str(self.description)
        return self._encode_str(player, des)

    def target(self, adict=None):
        """
        :param adict: The unpacked dictionary to prevent unnecessary unpacking
        :return: The target of the skill

         This is either 'e' for enemy, 'a' for ally (including self), 'f' for ally (excluding self) or 's' for self.
        """
        adict = self._unpack() if not adict else adict
        return adict['t']

    def damage(self, player, adict=None):
        """
        :param player: The player who is using the skill
        :param adict: The unpacked dictionary to prevent unnecessary unpacking
        :return: The damage range done
        """
        adict = self._unpack() if not adict else adict
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

    def precast(self, caster):
        """
        :param caster: The object representing the caster of the skill
        :return: A result indicating how many turns you gotta wait to use the kill
        """
        return self.time

    def precast_str(self, caster):
        """
        :param caster: The object representing the caster of the skill
        :return: A string representing exactly what is happening
        """
        des = str(self.precastdescription)
        return self._encode_str(caster, des)

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

         This does the skill on the specified target as cast by the caster
        """
        adict = self._unpack()
        dealt = self.cast_damage(caster, adict)
        caster.energy -= self.total_energy(caster, adict)
        target.health -= dealt
        des = str(self.actiondescription)
        return self._encode_str(caster, des, target, dealt)

    def postcast(self, caster):
        """
        :param caster: The object representing the caster of the skill
        :return: A result indicating how many turns you gotta wait before you can use it again
        """
        return self.recharge


if not Skill.table_exists():
    Skill.create_table(fail_silently=True)

    # Standard
    Skill.create(cclass=None, name="Attack", image="st-attack.png", energy=1, time=0, recharge=1,
                 action="t:e;d:5;di:0.2;ei:0.1", description="Your standard attack for [d] damage.",
                 actiondescription="[s] attack [t] with your weapon doing [d] damage!")
    Skill.create(cclass=None, name="Resurrect", image="st-resurrect.png", description="Resurrect downed ally.",
                 energy=5, time=1, recharge=-1, action="t:a;s:r;hp:50", actiondescription="You resurrect [t].")

    # Gunslinger
    Skill.create(cclass=1, name="Charged Shot", image="gs-charged.png", energy=2, time=1, recharge=2,
                 action="t:e;d:12;di:0.3;dd:2;ei:0.2", description="A charged shot for [d] damage.",
                 actiondescription="[s] hit [t] with a charged bolt for [d] damage.",
                 precastdescription="[s] is charging their gun for a shot!")
    Skill.create(cclass=1, name="Rapid Fire", image="gs-rapid.png", energy=2, time=0, recharge=1,
                 action="t:e;d:4;di:0.2;dd:2;ei:0.2", description="Shoot three rapid fire bullets for [d] damage each.",
                 actiondescription="[s] hit [t] with three bolts doing [d1], [d2] and [d3] damage.")
    Skill.create(cclass=1, name="Disrupting Blast", image="gs-disrupt.png", energy=1, time=0, recharge=1,
                 action="t:e;d:3;di:0.2;ei:0.2;c:dazed;cn:1;ci:0.1",
                 description="Disrupt target dealing [d] damage and Daze for [cn] turns.",
                 actiondescription="[s] hit [t] for [d] damage and cause Daze for [cn] turns.")
    Skill.create(cclass=1, name="Piercing Shot", image="gs-piercing.png", energy=2, time=0, recharge=2,
                 action="t:e;d:10;dd:2;di:0.3;ei:0.2;c:bleed;cn:1;ci:0.2",
                 description="Pierce target dealing [d] damage and Bleeding for [cn] turns.",
                 actiondescription="[s] hit [t] for [d] damage and causing Bleeding for [cn] turns.")
