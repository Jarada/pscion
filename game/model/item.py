#!/usr/bin/env python
# coding=utf-8
"""
item.py - Item database model
Copyright 2016, David Jarrett (wuufu.co.uk)

Characters can hold items in their inventory. These get created by the Story elements and Locations and added into
the users collection, usually with the addition of a UserFlag to prevent it being picked up twice.
"""

from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, user


class Item(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    player = ForeignKeyField(user.User, related_name="items")
    name = TextField()
    image = CharField()
    description = TextField()
    vital = BooleanField(default=False)
    price = IntegerField(default=0)

if not Item.table_exists():
    Item.create_table(fail_silently=True)