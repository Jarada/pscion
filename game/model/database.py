#!/usr/bin/env python
# coding=utf-8
"""
database.py - main Pscion database file
Copyright 2016, David Jarrett (wuufu.co.uk)

This is where Peewee resides. Peewee manages the storage of all
user based data; that is, stuff that you, the player, do in the
game. After all, we gotta store it somewhere...
"""

from peewee import SqliteDatabase, Model

conn = SqliteDatabase('pscion.db', threadlocals=True)
# import os
# print(os.getcwd())


class BaseModel(Model):
    class Meta:
        database = conn
