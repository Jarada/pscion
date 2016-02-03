#!/usr/bin/env python
# coding=utf-8
"""
database.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file is all about you. Yup! We store your username, password, and core character
information in the user model. Over models, such as the Inventory and Companions, will
reference what we have here.
"""

from peewee import ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, cclass


class User(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    username = TextField(unique=True)
    password = TextField()
    sesskey = TextField()
    character = TextField(null=True)
    charclass = ForeignKeyField(cclass.CharacterClass, null=True)
    charlevel = IntegerField(default=1)
    chargold = IntegerField(default=300)

if not User.table_exists():
    User.create_table(fail_silently=True)
