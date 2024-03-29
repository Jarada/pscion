"""
story.py - The central story class, all inherit
Copyright 2016, David Jarrett (wuufu.co.uk)

This contains the core class for managing the story elements within the game.
All necessary imports are linked here.
"""


class StoryElement:
    def __init__(self, major, minor, state, commands):
        self.major = major
        self.minor = minor
        self.state = state
        self.commands = commands
        self.default = "game.html"
        self.hidden = []
        self.unhide = None
        self.responses = None

    def json(self, player, additional=None):
        output = {"commands": []}
        if isinstance(additional, list):
            for command in additional:
                command.log(player)
                output["commands"].append(command.json)
        for command in self.commands:
            command.log(player)
            output["commands"].append(command.json)
        print("OUTPUT")
        print(output)
        return output

    def execute(self, player, action, output=None):
        return StoryPass([] if not output else output)

    def respond(self, player, response):
        return StoryPass([])

    def combat(self, player):
        return None


class StoryAdvancement:
    def __init__(self, major, minor, state, args, commands=None):
        self.major = major
        self.minor = minor
        self.state = state
        self.args = args
        self.commands = commands if commands else []


class StoryPass:
    def __init__(self, commands):
        self.commands = commands

    def json(self, player):
        output = {"commands": []}
        for command in self.commands:
            command.log(player)
            output["commands"].append(command.json)
        return output


class Story:
    def __init__(self):
        self.story = {}
        self.locations = {}
        self.combat = {}

    def add(self, major, minor, state, element):
        self.story["%d.%d:%d" % (major, minor, state)] = element

    def get(self, player):
        try:
            cls = self.story["%d.%d:%d" % (player.gamemajor, player.gameminor, player.gamestate)]
            return cls(player)
        except KeyError:
            return None

    def add_location(self, key, location):
        self.locations[key] = location

    def get_location(self, player, key):
        try:
            cls = self.locations[key]
            l = cls()
            travel = l.travel(player)
            if travel:
                for link in travel:
                    linkcls = self.locations[link]
                    l.linked.append(linkcls())
            return l
        except KeyError:
            return None

    def respond(self, player, level, state, response):
        try:
            return self.story["%d:%d" % (level, state)].respond(player, response)
        except KeyError:
            return None
