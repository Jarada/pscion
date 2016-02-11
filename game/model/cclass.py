#!/usr/bin/env python
# coding=utf-8
"""
cclass.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file contains core information about the classes used in the game. Most characters have two classes, a primary
and a secondary class. Some classes can only be picked to be the secondary class.

Characters can load both primary and secondary skills of their primary class but only non-primary skills of their
secondary class.
"""

from peewee import BooleanField, PrimaryKeyField, TextField
from game.model import database


class CharacterClass(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    name = TextField(unique=True)
    primary = BooleanField(default=True)
    description = TextField()


if not CharacterClass.table_exists():
    CharacterClass.create_table(fail_silently=True)
    CharacterClass.create(name="Gunslinger", description="Master of the gun")
    CharacterClass.create(name="Dueler", description="Master of the vibroblade")
    CharacterClass.create(name="Rogue", description="Master of stealth and deception")
    CharacterClass.create(name="Ranger", description="Master of explosive strength")
    CharacterClass.create(name="Doctor", primary=False, description="Master of healing")
    CharacterClass.create(name="Jumper", primary=False, description="Master of phased attacks")