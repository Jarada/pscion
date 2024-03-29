#!/usr/bin/env python
# coding=utf-8
"""
user.py - User database model
Copyright 2016, David Jarrett (wuufu.co.uk)

This file is all about you. Yup! We store your username, password, and core character information in the user model.
Over models, such as the Inventory and Companions, will reference what we have here.
"""

from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, PrimaryKeyField, TextField, SelectQuery
from game.model import database, cclass, skill
import hashlib


class User(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()
    sesskey = CharField()
    name = CharField(null=True)
    pclass = ForeignKeyField(cclass.CharacterClass, null=True, related_name="playerprimary")
    sclass = ForeignKeyField(cclass.CharacterClass, null=True, related_name="playersecondary")
    level = IntegerField(default=1)
    exp = IntegerField(default=0)
    gold = IntegerField(default=0)
    health = IntegerField(default=200)
    maxhealth = IntegerField(default=200)
    energy = IntegerField(default=10)
    maxenergy = IntegerField(default=10)
    gamemajor = IntegerField(default=0)
    gameminor = IntegerField(default=0)
    gamestate = IntegerField(default=0)
    gameargs = TextField(null=True)
    location = CharField(default="home")

    def initial(self):
        skindex = 1  # Workaround for Peewee Issue #388 https://github.com/coleifer/peewee/issues/388
        for sk in skill.Skill.select().order_by(skill.Skill.pid):
            if sk.pid != skindex:
                continue
            if sk.pid == 1 or sk.pid == 2:
                UserSkill.create(user=User.get(User.username == self.username), skill=sk, equipped=sk.pid)
            else:
                UserSkill.create(user=User.get(User.username == self.username), skill=sk)
            skindex += 1

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
        from game.commands.command import SetElementStatus, UpdateLocationActions, SetResponses
        output = {"commands": []}
        if element.responses:
            output["commands"].append(SetResponses(element.responses).json)
        else:
            output["commands"].append(UpdateLocationActions().json)
        if element.unhide:
            output["commands"].append(SetElementStatus(element.unhide, True).json)
        return output

    def earlier(self, major, minor, state):
        """
        :param major: The major part of the story
        :param minor: The minor part of the story
        :param state: The state part of the story
        :return: If the chosen major, minor and state are earlier in time than the player
        """
        return self.gamemajor <= major and self.gameminor <= minor and self.gamestate < state

    def later_eq(self, major, minor, state):
        """
        :param major: The major part of the story
        :param minor: The minor part of the story
        :param state: The state part of the story
        :return: If the chosen major, minor and state are equal to or later in time than the player
        """
        return self.gamemajor >= major and self.gameminor >= minor and self.gamestate >= state

    def health_percent(self):
        """
        :return: The percentage health of the user
        """
        return int((float(self.health) / float(self.maxhealth)) * 100)

    def energy_percent(self):
        """
        :return: The percentage energy of the user
        """
        return int((float(self.energy) / float(self.maxenergy)) * 100)

    def skill(self, slot):
        """
        :param slot: The skill slot (1-4) to get the user's skill for
        :return: The skill (if present), or None
        """
        result = self.skills.select().where(UserSkill.equipped == slot)
        if result.count() > 0:
            return result.get()
        return None

    def class_skills(self):
        """
        :return: All available skills for the users selected Primary/Secondary classes
        """
        result = self.skills.select(UserSkill, skill.Skill).join(skill.Skill)
        output = []
        for sk in result:
            if ((sk.skill.cclass is None or sk.skill.cclass == self.pclass) and sk.skill.primary == True) or \
                    (sk.skill.cclass == self.sclass and sk.skill.primary == False):
                output.append(sk)
        return output

    def equip(self, upid, slot):
        """
        :param upid: The skill to equip
        :param slot: The slot to put the skill
        :return: If the equip was successful
        """
        try:
            existing = self.skills.select().where(UserSkill.equipped == slot).get()
            if existing:
                existing.equipped = 0
                existing.save()
        except Exception:
            pass
        skill = self.skills.select().where(UserSkill.pid == upid).get()
        if skill:
            skill.equipped = slot
            skill.save()
            return True
        return False

    def unequip(self, upid):
        """
        :param upid: The skill to unequip
        :return: If the unequip was successful
        """
        skill = self.skills.select().where(UserSkill.pid == upid).get()
        if skill:
            skill.equipped = 0
            skill.save()
            return True
        return False

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

    def item_for_inventory(self, olist, row, col):
        """
        :param olist: The list of items; this allows items to be ordered
        :param row: The row in the Inventory list to fill
        :param col: The column in the Inventory list to fill
        :return: The item (if present), or None
        """
        index = (row * 11) + col
        if isinstance(olist, list) and len(olist) > index:
            return olist[index]
        if isinstance(olist, SelectQuery) and olist.count() > index:
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


class UserSkill(database.BaseModel):
    pid = PrimaryKeyField(primary_key=True)
    user = ForeignKeyField(User, related_name="skills")
    skill = ForeignKeyField(skill.Skill, related_name="users")
    equipped = IntegerField(default=0)


if not User.table_exists():
    User.create_table(fail_silently=True)
    User.create(username="Wuufu", password=hashlib.md5(b"blah").hexdigest(), sesskey="", name="Wuufu", pclass=1)
if not UserFlag.table_exists():
    UserFlag.create_table(fail_silently=True)
if not UserLog.table_exists():
    UserLog.create_table(fail_silently=True)
if not UserSkill.table_exists():
    UserSkill.create_table(fail_silently=True)
    index = 1  # Workaround for Peewee Issue #388 https://github.com/coleifer/peewee/issues/388
    for sk in skill.Skill.select().order_by(skill.Skill.pid):
        if sk.pid != index:
            continue
        if sk.pid == 1 or sk.pid == 2:
            UserSkill.create(user=User.get(User.username == "Wuufu"), skill=sk, equipped=sk.pid)
        else:
            UserSkill.create(user=User.get(User.username == "Wuufu"), skill=sk)
        index += 1
