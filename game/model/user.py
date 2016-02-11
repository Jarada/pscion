#!/usr/bin/env python
# coding=utf-8
"""
user.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file is all about you. Yup! We store your username, password, and core character information in the user model.
Over models, such as the Inventory and Companions, will reference what we have here.
"""

from peewee import CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField
from game.model import database, cclass


class User(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()
    sesskey = CharField()
    character = CharField(null=True)
    charpclass = ForeignKeyField(cclass.CharacterClass, null=True, related_name="playerprimary")
    charsclass = ForeignKeyField(cclass.CharacterClass, null=True, related_name="playersecondary")
    charlevel = IntegerField(default=1)
    chargold = IntegerField(default=0)
    charhealth = IntegerField(default=200)
    charmaxhealth = IntegerField(default=200)
    charenergy = IntegerField(default=10)
    charmaxenergy = IntegerField(default=10)
    gamemajor = IntegerField(default=0)
    gameminor = IntegerField(default=0)
    gamestate = IntegerField(default=0)
    gameargs = TextField(null=True)
    location = CharField(default="home")

    def add_log(self, msgcmd):
        """
        :param msgcmd: The SendMessage object
        """
        log = UserLog.create(user=self, sender=msgcmd.sender, msg=msgcmd.msg)
        if msgcmd.eclass:
            log.eclass = msgcmd.eclass
        log.save()
        # TODO Limit to 50 log entries

    def json_logs(self, element):
        """
        :param element: The Story element
        :return: The JSON representing the log entries in the system

        This function is called to setup the UI from a cold boot, with the update of location actions
        and the relevant element's hidden/unhidden.
        """
        from game.commands.command import SetElementStatus, UpdateLocationActions
        output = {"commands": [UpdateLocationActions().json]}
        if element.unhide:
            command = SetElementStatus(element.unhide, True)
            output["commands"].append(command.json)
        return output

    def health_percent(self):
        """
        :return: The percentage health of the user
        """
        return int((float(self.charhealth) / float(self.charmaxhealth)) * 100)

    def energy_percent(self):
        """
        :return: The percentage energy of the user
        """
        return int((float(self.charenergy) / float(self.charmaxenergy)) * 100)

    def add_flag(self, major, minor, state, flag, result=None):
        """
        :param major: The major step of the story (*all 0 if global)
        :param minor: The minor step of the story (*all 0 if global)
        :param state: The state step of the story (*all 0 if global)
        :param flag: The unique flag to represent an occurrence
        :param result: The result of the flag (if applicable)
        :return:
        """
        stored = self.get_flag(major, minor, state, flag)
        if stored:
            if result:
                flag.result = result
                flag.save()
        else:
            UserFlag.create(user=self, major=major, minor=minor, state=state, flag=flag, result=result)

    def get_flag(self, major, minor, state, flag):
        """
        :param major: The major step of the story (*all 0 if global)
        :param minor: The minor step of the story (*all 0 if global)
        :param state: The state step of the story (*all 0 if global)
        :param flag: The unique flag to represent an occurrence
        :return: The UserFlag object if found, or None if not found
        """
        try:
            return UserFlag.get(UserFlag.user==self, UserFlag.major==major, UserFlag.minor==minor,
                                UserFlag.state==state, UserFlag.flag==flag)
        except:
            return None

    def flag(self, major, minor, state, flag):
        """
        :param major: The major step of the story (*all 0 if global)
        :param minor: The minor step of the story (*all 0 if global)
        :param state: The state step of the story (*all 0 if global)
        :param flag: The unique flag to represent an occurrence
        :return: The result of the flag or True if found, or False if not found
        """
        flag = self.get_flag(major, minor, state, flag)
        if flag and flag.result:
            return flag.result
        elif flag:
            return True
        return False

    def ordered_items(self):
        olist = []
        for item in self.items:
            olist.append(item)
        return olist

    def item_for_inventory(self, olist, row, col):
        index = (row * 11) + col
        if len(olist) > index:
            return olist[index]
        return None


class UserFlag(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    user = ForeignKeyField(User, related_name="flags")
    major = IntegerField(index=True)
    minor = IntegerField(index=True)
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
    User.create(username="Wuufu", password="blah", sesskey="", character="Wuufu", charpclass=1)
if not UserFlag.table_exists():
    UserFlag.create_table(fail_silently=True)
if not UserLog.table_exists():
    UserLog.create_table(fail_silently=True)
