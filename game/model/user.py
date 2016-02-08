#!/usr/bin/env python
# coding=utf-8
"""
database.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file is all about you. Yup! We store your username, password, and core character
information in the user model. Over models, such as the Inventory and Companions, will
reference what we have here.
"""

from peewee import CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, cclass


class User(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()
    sesskey = CharField()
    character = CharField(null=True)
    charclass = ForeignKeyField(cclass.CharacterClass, null=True)
    charlevel = IntegerField(default=1)
    chargold = IntegerField(default=300)
    gamemajor = IntegerField(default=0)
    gameminor = IntegerField(default=0)
    gamestate = IntegerField(default=0)
    gameargs = TextField(null=True)
    location = CharField(default="home")

    def add_log(self, msgcmd):
        log = UserLog.create(user=self, sender=msgcmd.sender, msg=msgcmd.msg)
        if msgcmd.eclass:
            log.eclass = msgcmd.eclass
        log.save()
        # TODO Limit to 50 log entries

    def json_logs(self, element):
        from game.commands.command import SendMessage, SetElementStatus
        output = {"commands": []}
        if element.unhide:
            command = SetElementStatus(element.unhide, True)
            output["commands"].append(command.json)
        for log in self.logs:
            command = SendMessage(log.sender, log.msg, 0, log.eclass)
            output["commands"].append(command.json)
        return output

    @staticmethod
    def flag(self, level, state, flag):
        flag = UserFlag.get(level==level, state==state, flag==flag)
        if flag and flag.result:
            return flag.result
        elif flag:
            return True
        return False


class UserFlag(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    user = ForeignKeyField(User, related_name="flags")
    level = IntegerField(index=True)
    state = IntegerField(index=True)
    flag = TextField(index=True)
    result = TextField(null=True)


class UserLog(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    user = ForeignKeyField(User, related_name="logs")
    sender = CharField(null=True)
    msg = TextField()
    eclass = CharField(null=True)


if not User.table_exists():
    User.create_table(fail_silently=True)
    User.create(username="Wuufu", password="blah", sesskey="", character="Wuufu", charclass=1)
if not UserFlag.table_exists():
    UserFlag.create_table(fail_silently=True)
if not UserLog.table_exists():
    UserLog.create_table(fail_silently=True)
