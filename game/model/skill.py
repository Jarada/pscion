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

from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, cclass


class Skill(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    cclass = ForeignKeyField(cclass.CharacterClass, related_name="skills")
    primary = BooleanField(default=True)
    name = TextField()
    image = CharField()
    description = TextField()
    energy = IntegerField()
    time = IntegerField()
    recharge = IntegerField()
    action = TextField()
    actiondescription = TextField()

    def unpack(self):
        """
        :return: An unpacked dictionary of the skill

         The skill stores data in the database related to what the skill does including the target and the skills
         actions. This is stored in a single string. This function unpacks that string and turns it into a
         dictionary that is returned.
        """
        actsplit = str(self.action).split(";")
        actdict = {}
        for keyvalue in actsplit:
            keyvaluesplit = keyvalue.split(":")[0]
            actdict[keyvaluesplit[0]] = keyvaluesplit[1]
        return actdict

    def target(self):
        """
        :return: The target of the skill

         This is either 'e' for enemy, 'a' for ally (including self) or 's' for self.
        """
        actdict = self.unpack()
        return actdict['t']

    def cast(self, caster, target):
        """
        :param caster: The object representing the caster of the skill
        :param target: The object representing the target of the skill
        :return: A string representing the action that has occurred

         This does the skill on the specified target as cast by the caster
        """
        pass


if not Skill.table_exists():
    Skill.create_table(fail_silently=True)

    # Standard
    Skill.create(cclass=None, name="Attack", image="attack", description="Your standard attack.", energy=1, time=0,
                 recharge=1, action="t:e;d:5;di:0.2",
                 actiondescription="You attack [t] with your weapon doing [d] damage!")
    Skill.create(cclass=None, name="Resurrect", image="resurrect", description="Resurrect downed ally.", energy=5,
                 time=1, recharge=-1, action="t:a;s:r;hp:50", actiondescription="You resurrect [t].")

    # Gunslinger
