"""
database.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file contains core information about the classes used in the game.
Most characters have two classes, a primary and a secondary class.
"""

from peewee import BooleanField, PrimaryKeyField, TextField
from game.model import database


class CharacterClass(database.BaseModel):
    cid = PrimaryKeyField(primary_key=True)
    name = TextField(unique=True)
    primary = BooleanField(default=False)
