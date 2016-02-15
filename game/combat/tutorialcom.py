"""
tutorialcom.py - Enemies during the Tutorial
Copyright 2016, David Jarrett (wuufu.co.uk)

This class contains all enemies used during the tutorial phase.
"""

import random
from game.combat.combat import Enemy, EnemyAttack


class BullyEnemy(Enemy):
    def __init__(self, player):
        super().__init__(player, "Bully", 20, 10, [
            EnemyAttack("Punch", "[s] punches [t] dealing [d] damage.", "p", 2, {"d": 10, "dd": 5}),
            EnemyAttack("Kick", "[s] kicks [t] dealing [d] damage.", "p", 2, {"d": 12, "dd": 5})
        ])

    def action(self, player):
        if self.energy > 1:
            attack = random.choice(self.attacks)
            return attack.cast(self, player)
        elif self.energy == 0:
            return self.rest()
