"""
combat.py - Deals with combat
Copyright 2016, David Jarrett (wuufu.co.uk)

Combat works in turns. The person to go first depends on the story and how the enemies were found. On the enemies
turns, they all choose an action based upon their energy levels, health and from the list of attacks available to
them.
"""

import math, random
from game.commands.command import CombatError, CombatMessage, CombatUpdate


class Combat:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.turn = 'e' if enemies.first else 'p'
        self.tutorial = False
        self.casting = []
        self.recharging = []

    def _load_skill_target(self, args):
        result = []
        for skillarg in args:
            # We get arguments in the format ('skill-[person]-[index]', 'target-[person]-[index]')
            targetarg = args[skillarg]
            print('Combat ACT %s %s' % (str(skillarg), str(targetarg)))
            skillsplit = skillarg.split('-')
            targetsplit = targetarg.split('-')

            caster = None
            skill = None
            target = None
            targettypes = []

            if skillsplit[1] == 'player':
                caster = self.player
                skill = self.player.skill(int(skillsplit[2]))

            if targetsplit[1] == 'enemy':
                target = self.enemies.enemies[int(targetsplit[2]) - 1]
                targettypes = ['e']

            result.append({'caster': caster, 'skill': skill, 'target': target, 'skillid': skillarg,
                           'targettypes': targettypes})
        return result

    def start(self):
        """
        :return: The starting CombatMessage that gets displayed on start
        """
        if self.turn == 'e':
            ene = "enemies take" if len(self.enemies.enemies) > 0 else "enemy takes"
            self.turn = 'p'
            return [CombatMessage("The %s the initiative!" % ene, 'start')]
        else:
            return [CombatMessage("You take the initiative! It's your turn.", 'start')]

    def act_turn(self, args):
        """
        :param args: The arguments representing the players action on this turn
        :return: The results of the turn, including player and enemy actions
        """
        act = []
        if self.turn == 'p':
            actions = self._load_skill_target(args)
            errors = []
            recharged = []

            # Validate
            for action in actions:
                atarget = action['skill'].skill.target()
                if atarget not in action['targettypes']:
                    errors.append(action['skillid'])

            # Process
            if len(errors) > 0:
                return [CombatError(errors).json]

            for cast in self.casting:
                action = cast['action']
                skill = action['skill'].skill
                eclass = 'player' if 'player' in action['skillid'] else 'companion'
                cast['time'] -= 1
                if cast['time'] == 0:
                    cmsg = CombatMessage(skill.cast(action['caster'], action['target']), eclass)
                    cmsg.recharging(action['skillid'])
                    act.append(cmsg.json)
                    self.casting.remove(cast)
                    self.recharging.append({'action': action, 'time': skill.postcast(action['caster'])})
                else:
                    act.append(CombatMessage(skill.precast_str(action['caster'])).json, eclass)

            for cast in self.recharging:
                action = cast['action']
                skill = action['skill'].skill
                eclass = 'player' if 'player' in action['skillid'] else 'companion'
                cast['time'] -= 1
                if cast['time'] == 0:
                    cmsg = CombatMessage(skill.recharged_str(), eclass)
                    cmsg.recharged(action['skillid'])
                    recharged.append(cmsg.json)
                    self.recharging.remove(cast)

            for action in actions:
                skill = action['skill'].skill
                eclass = 'player' if 'player' in action['skillid'] else 'companion'
                if skill.precast(action['caster']) > 0:
                    cmsg = CombatMessage(skill.precast_str(action['caster']), eclass)
                    cmsg.locked(action['skillid'])
                    act.append(cmsg.json)
                    self.casting.append({'action': action, 'time': skill.precast(action['caster'])})
                else:
                    cmsg = CombatMessage(skill.cast(action['caster'], action['target']), eclass)
                    cmsg.recharging(action['skillid'])
                    act.append(cmsg.json)
                    self.recharging.append({'action': action, 'time': skill.postcast(action['caster'])})

            act.extend(recharged)
        act.extend(self.enemies.actions(self.player))
        update = CombatUpdate()
        for idx, val in enumerate(self.enemies.enemies):
            update.add_update('enemy-%d' % (idx + 1), 'health', val.health, val.health_percent())
            update.add_update('enemy-%d' % (idx + 1), 'energy', val.energy, val.energy_percent())
        update.add_update('player', 'health', self.player.health, self.player.health_percent())
        update.add_update('player', 'energy', self.player.energy, self.player.energy_percent())
        act.append(update.json)
        self.turn = 'p'
        return act


class Enemies:
    def __init__(self, enemies, first=False):
        self.enemies = enemies
        self.first = first

    def actions(self, player):
        """
        :param player: The player object
        :return: The result of the enemies acting
        """
        actions = []
        for enemy in self.enemies:
            actions.append(CombatMessage(enemy.action(player), 'enemy').json)
        return actions


class Enemy:
    def __init__(self, player, name, health, energy, attacks):
        self.player = player
        self.name = name
        self.health = health
        self.maxhealth = health
        self.energy = energy
        self.maxenergy = energy
        self.attacks = attacks

    def rest(self):
        """
        :return: The enemy is resting; no attacks were made
        """
        return "%s is resting." % self.name

    def action(self, player):
        """
        :param player: The player object
        :return: The results of the enemy acting
        """
        pass

    def health_percent(self):
        """
        :return: The percentage health of the enemy
        """
        return int((float(self.health) / float(self.maxhealth)) * 100)

    def energy_percent(self):
        """
        :return: The percentage energy of the enemy
        """
        return int((float(self.energy) / float(self.maxenergy)) * 100)


class EnemyAttack:
    def __init__(self, name, actdes, target, energy, action, time=0):
        self.name = name
        self.actdes = actdes
        self.target = target  # Either f for friendly, p for player, c for companion or a for party
        self.energy = energy
        self.action = action
        self.time = time

    def damage(self, enemy):
        """
        :param player: The enemy who is using the skill
        :return: The damage range done
        """
        player = enemy.player
        if 'd' in self.action:
            d = float(self.action['d'])
            if 'di' in self.action and player.level > 1:
                l = player.level - 1
                d = math.floor(d + (l * float(self.action['di'])))
            if 'dd' in self.action:
                db = d - float(self.action['dd'])
                dt = d + float(self.action['dd'])
                return "%d|%d" % (int(db), int(dt))
            else:
                return "%d" % int(d)
        return "%d" % 0

    def total_energy(self, player):
        """
        :param player: The player who is using the skill
        :return: The total energy usage of the skill
        """
        if 'ei' in self.action:
            l = player.level - 1
            return math.floor(float(self.energy) + (l * float(self.action['ei'])))
        return self.energy

    def precast(self):
        """
        :return: A result indicating how many turns it takes to cast
        """
        return self.time

    def cast_damage(self, caster):
        """
        :param caster: The object representing the caster of the skill
        :return: The number of damage done randomly chosen with available guidelines
        """
        dmg = self.damage(caster)
        dmsplit = dmg.split("|")
        print(dmsplit)
        if len(dmsplit) == 2:
            return random.randint(int(dmsplit[0]), int(dmsplit[1]))
        else:
            return int(dmsplit[0])

    def cast(self, caster, target):
        """
        :param caster: The object representing the caster of the skill
        :param target: The object representing the target of the skill
        :return: A string representing the action that has occurred

         This does the EnemyAttack on the specified target as cast by the caster
        """
        dealt = self.cast_damage(caster)
        caster.energy -= self.total_energy(caster)
        target.health -= dealt
        # TODO ADD SPAN CLASSES FOR STYLING
        des = self.actdes.replace('[s]', caster.name)
        des = des.replace('[t]', target.name)
        des = des.replace('[d]', str(dealt))
        return des
