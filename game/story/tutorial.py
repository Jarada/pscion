"""
tutorial.py - The tutorial story area
Copyright 2016, David Jarrett (wuufu.co.uk)

With there being a disconnect between the server and the client, there comes a desire
for the server to be able to send commands to the client and have them executed in
Javascript. These include things like showing/hiding UI elements, adding textual messages,
adjusting the actions dropdown, playing sounds, and so forth.

This is all dealt with by the Command classes indicated below.
"""

from game.story import story
from game.commands import command


class TutorialZero(story.StoryElement):
    def __init__(self, player):
        super().__init__(0, 0, 0, [
            command.Wait(2000),
            command.SetElementStatus(".central-wrap", True),
            command.SendMessage("Zaphyr", "Hey! Hey! Wake up! It's time to get up!", 4000, "zaphyr"),
            command.SendMessage(None, "...", 4000),
            command.SendMessage("Zaphyr", "Hey! Hey! Really, you're gonna be late for work here...", 4000, "zaphyr"),
            command.SendMessage(None, "...", 4000),
            command.SendSound("Bzzt", 0),
            command.SendMessage(None, "BZZT!", 500),
            command.SendMessage("Zaphyr", "Come on now! I gotta buzz you? Use the dropdown to the right to give me some kind of response.", 0, "zaphyr"),
            command.SetElementStatus(".sidebar-wrap, #top-row", True),
            command.SetResponses({"aaargh": "Aaargh!", "more": "More sleep!", "school": "Don't wanna go to school!"})
        ])
        self.hidden = ["#menu", "#top-row", ".central-wrap", ".sidebar-wrap"]
        self.unhide = ".central-wrap .sidebar-wrap #top-row"

    def respond(self, player, response):
        return story.StoryAdvancement(0, 0, 1, response)


class TutorialOne(story.StoryElement):
    def __init__(self, player):
        super().__init__(0, 0, 1, [])
        result = player.gameargs
        if result == "aaargh":
            self.commands.append(command.SendMessage(player.character, "Aaargh!", 3000, "player"))
            self.commands.append(command.SendMessage("Zaphyr", "That's all you can give me? Really?!?", 3000, "zaphyr"))
        elif result == "more":
            self.commands.append(command.SendMessage(player.character, "More Sleep!", 3000, "player"))
            self.commands.append(command.SendMessage("Zaphyr", "You've slept for hours! Come on, it's really time to get up.", 3500, "zaphyr"))
        elif result == "school":
            self.commands.append(command.SendMessage(player.character, "Don't wanna go to school!", 3000, "player"))
            self.commands.append(command.SendMessage("Zaphyr", "You're not that young! You've grown enough you are actually working for a change.", 4000, "zaphyr"))
        self.commands.extend([
            command.UpdateLocationActions(),
            command.SendMessage("Zaphyr", "Let's try something else.", 4000, "zaphyr"),
            command.SendMessage("Zaphyr", "Perhaps if you open your eyes and look around your room, you'll feel more awake. Use the dropdown and try it now!", 0, "zaphyr")
        ])
        self.hidden = ["#menu"]

    def execute(self, player, action, output=None):
        if action == 'look':
            return story.StoryAdvancement(0, 0, 2, None, output)


class TutorialTwo(story.StoryElement):
    def __init__(self, player):
        super().__init__(0, 0, 2, [
            command.UpdateLocationActions(),
            command.SendMessage("Zaphyr", "Well, it's not much, but it's home.", 2000, "zaphyr"),
            command.SendMessage("Zaphyr", "Now, I'll let you explore your home a little. Use the dropdown to examine and pickup things, and the buttons to the left to sort out your own inventory.", 6000, "zaphyr"),
            command.SendMessage("Zaphyr", "What?! I don't see any buttons. Hmm. Hold up, let me adjust your display...", 4000, "zaphyr"),
            command.SendMessage("Zaphyr", "Almost there...", 3000, "zaphyr"),
            command.SetElementStatus("#menu", True),
            command.Wait(450),
            command.SendMessage("Zaphyr", "There you go! Now when you're done, click the 'Home' text at the top and select to move out into the corridor.", 2000, "zaphyr")
        ])
        self.hidden = ["#menu"]
        self.unhide = "#menu"

    def execute(self, player, action, output=None):
        if action == 'look':
            return story.StoryAdvancement(0, 0, 2, None, output)


def load(storyobj):
    storyobj.add(0, 0, 0, TutorialZero)
    storyobj.add(0, 0, 1, TutorialOne)
    storyobj.add(0, 0, 2, TutorialTwo)
