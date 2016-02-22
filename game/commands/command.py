"""
command.py - Deals with server commands
Copyright 2016, David Jarrett (wuufu.co.uk)

With there being a disconnect between the server and the client, there comes a desire
for the server to be able to send commands to the client and have them executed in
Javascript. These include things like showing/hiding UI elements, adding textual messages,
adjusting the actions dropdown, playing sounds, and so forth.

This is all dealt with by the Command classes indicated below.
"""

from flask import render_template


class Command:
    def __init__(self, json):
        self.json = json

    def json(self):
        return self.json

    def log(self, player):
        pass


class Wait(Command):
    def __init__(self, time):
        super().__init__({"type": "wait", "time": time})


class LockUI(Command):
    def __init__(self, lock):
        super().__init__({"type": "lock", "lock": lock})


class LoadCentralContent(Command):
    def __init__(self, template):
        super().__init__({"type": "central", "html": render_template(template)})


class SetElementStatus(Command):
    def __init__(self, element, status):
        super().__init__({"type": "status", "element": element, "status": status})


class SetActionBarStatus(Command):
    def __init__(self, status):
        super().__init__({"type": "actbarstatus", "status": status})


class SetResponses(Command):
    def __init__(self, responses):
        super().__init__({"type": "responses", "responses": responses})


class SendMessage(Command):
    def __init__(self, sender, msg, time, eclass=None):
        super().__init__({"type": "msg", "sender": sender, "msg": msg, "time": time})
        self.sender = sender
        self.msg = msg
        self.eclass = eclass
        if eclass:
            self.json["eclass"] = eclass

    def log(self, player):
        player.add_log(self)


class SendSound(Command):
    def __init__(self, sound, time):
        super().__init__({"type": "sound", "sound": sound, "time": time})


class UpdateLocationActions(Command):
    def __init__(self):
        super().__init__({"type": "localeact"})


class UpdateLocationTravel(Command):
    def __init__(self):
        super().__init__({"type": "localetravel"})


class UpdateLocationName(Command):
    def __init__(self, name):
        super().__init__({"type": "location", "name": name})


class ClearActionBar(Command):
    def __init__(self):
        super().__init__({"type": "clearbar"})


class StartCombat(Command):
    def __init__(self):
        super().__init__({"type": "combat"})


class CombatMessage(Command):
    def __init__(self, msg, eclass=None):
        super().__init__({"type": "cmsg", "msg": msg, "time": 600})
        self.msg = msg
        self.eclass = eclass
        if eclass:
            self.json["eclass"] = eclass

    def locked(self, locked):
        self.json["locked"] = locked

    def recharging(self, recharge):
        self.json["recharge"] = recharge

    def recharged(self, recharged):
        self.json["recharged"] = recharged


class CombatUpdate(Command):
    def __init__(self):
        super().__init__({"type": "combatupdate", "updates": []})

    def add_update(self, target, source, value, percent):
        self.json["updates"].append({"target": target, "source": source, "value": value, "percent": percent})


class CombatError(Command):
    def __init__(self, errors):
        super().__init__({"type": "combaterr", "errors": errors,
                          "msg": "One or more skills have invalid targets. Please fix these and try again."})
