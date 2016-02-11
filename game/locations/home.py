"""
story.py - The central story class, all inherit
Copyright 2016, David Jarrett (wuufu.co.uk)

Home Sweet Home
"""

from game.locations import location
from game.commands.command import SendMessage, UpdateLocationActions
from game.model.item import Item


class Home(location.Location):
    def __init__(self):
        super().__init__("home", "Home")

    def actions(self, player):
        if player.gamemajor == 0 and player.gameminor == 0 and player.gamestate == 1:
            return [location.Location.ACT_LOOK]
        elif player.gamemajor == 0 and player.gameminor == 0 and player.gamestate > 1:
            result = [location.Location.ACT_LOOK]
            if not player.flag(0,0,2,"ebook"):
                result.append(self._act_examine("book", "Book"))
            elif not player.flag(0,0,2,"pbook"):
                result.append(self._act_examine("book", "Book"))
                result.append(self._act_pickup("book", "Book"))
            if not player.flag(0,0,2,"echip"):
                result.append(self._act_examine("chip", "Credit chip"))
            elif not player.flag(0,0,2,"pchip"):
                result.append(self._act_examine("chip", "Credit chip"))
                result.append(self._act_pickup("chip", "Credit chip"))
            result.extend([self._act_examine("lamp", "Lamp"), self._act_examine("sofa", "Sofa")])
            return result

    def examine(self, player, item):
        print(item)
        if item == "book":
            player.add_flag(0,0,2,"ebook")
            return [SendMessage("", "'To Kill a Mockinghawk' by Kylie Ren. An interesting read so far, you hope "
                                    "you'll have some time to finish the book amid the work you have to do.", 0),
                    UpdateLocationActions()]
        if item == "chip":
            player.add_flag(0,0,2,"echip")
            return [SendMessage("", "A Credit chip from yesterday's pay day. Has appropriate money's to add to your "
                                    "balance. You should pick this up before you leave so you actually have some "
                                    "cash.", 0),
                    UpdateLocationActions()]
        if item == "lamp":
            return [SendMessage("", "It's a rather stylish lamp you picked up at a local car boot sale. Except "
                                    "there were no cars or boots in the sale. You wonder why it's still called "
                                    "that.", 0)]
        if item == "sofa":
            if not player.flag(0,0,2,"pbook"):
                return [SendMessage("", "It's a sofa. Made of dark leather, it has a book on it and is rather comfy "
                                    "to sit on. Perhaps you should stop looking at it?", 0)]
            else:
                return [SendMessage("", "It's a sofa. Made of dark leather it looks rather comfy to sit on, but you "
                                        "have other things to do today. Perhaps you should stop looking at it?", 0)]

    def pickup(self, player, item):
        if item == "book":
            player.add_flag(0,0,2,"pbook")
            Item.create(name="Book: 'To Kill a Mockinghawk' by Kylie Ren", image="bookhawk.png",
                        description="An interesting read so far, you hope you'll have some time to finish the book "
                                    "amid the work you have to do.", price=15, player=player)
            return [SendMessage("", "You pickup the book and put it in your bag.", 0),
                    UpdateLocationActions()]
        if item == "chip":
            player.add_flag(0,0,2,"pchip")
            player.chargold += 200
            player.save()
            return [SendMessage("", "You pickup the Credit chip and gain 200 credits.", 0),
                    UpdateLocationActions()]

    def look(self, player):
        start = player.gamemajor == 0 and player.gameminor == 0 and player.gamestate == 1
        if not player.flag(0, 0, 2, "pbook"):
            book = "with a book laid on it,"
        else:
            book = ""
        if not player.flag(0,0,2,"pchip"):
            chip = " There is a Credit chip on the floor."
        else:
            chip = ""
        return [SendMessage("", "The room is sparsely decorated. You have your bed in the corner, with a bedside "
                                "cabinet upon which a lamp is placed. There is a sofa just next to this " + book +
                            " and a TV on the far wall. Two doors either side of the TV lead to the kitchen and "
                            "bathroom respectively, and a door to the left leads to the exit." + chip,
                            14000 if start else 0)]
