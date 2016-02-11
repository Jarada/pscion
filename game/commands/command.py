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


class ClearActionBar(Command):
    def __init__(self):
        super().__init__({"type": "clearbar"})

