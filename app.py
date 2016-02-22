#!/usr/bin/env python
# coding=utf-8
"""
app.py - main Pscion app file
Copyright 2016, David Jarrett (wuufu.co.uk)

Welcome! This is the entry point of the application, where great things start.
The main purpose of this file is to act as the web server for the game, and
to provide a link between you, the player, and the game engine.

The entire thing is managed by Flask, a useful web microframework that allows
fast deployment of web services. Feel free to browse below; most things are
self explanatory but I've added comments where I feel they'll benefit.
"""

from flask import Flask, abort, jsonify, render_template, redirect, request, session, url_for
from game.combat.combat import Combat
from game.model import user, cclass
from game.story import story, tutorial
import game.story.load as sload
import game.locations.load as lload
import uuid

# This initialises the web server; it is started at the bottom of this file
app = Flask(__name__)

# We pull in the story here and load in all story elements
gstory = story.Story()
sload.load(gstory)
lload.load(gstory)


def player():
    if 'userid' in session and 'sesskey' in session:
        try:
            return user.User.get(user.User.pid == session['userid'], user.User.sesskey == session['sesskey'])
        except:
            pass
    return None


def element():
    return gstory.get(player())


def location():
    return gstory.get_location(player(), player().location)


# Routes indicate what URL is needed for a function to be called.
# In this case, it's the root directory, or pscion.wuufu.co.uk.
@app.route('/')
def index():
    p = player()
    if p:
        # Return Game Page
        e = element()
        l = location()
        return render_template("game.html", player=player(), content="layouts/%s" % e.default, element=e, location=l)
    else:
        # Return Login Page
        return render_template("login.html")


@app.route('/q/logintemp')
def login_temp():
    # Return Login Form
    return render_template("parts/login-login.html")


@app.route('/q/login', methods=['POST'])
def login():
    # Check login
    if 'username' in request.form and 'password' in request.form:
        print(request.form)
        try:
            p = user.User.get(user.User.username == request.form['username'],
                              user.User.password == request.form['password'])
            print(p)
            p.sesskey = str(uuid.uuid4())
            print(p)
            p.save()
            print(p)
            session['userid'] = p.pid
            print(type(p.pid).__name__)
            session['sesskey'] = str(p.sesskey)
            print(type(p.sesskey).__name__)
            return '', 200
        except Exception as e:
            print(e)
            pass
    return abort(403)


@app.route('/logout')
def logout():
    # Set Logout
    session.clear()
    return redirect(url_for('index'))


@app.route('/q/registertemp')
def register_temp():
    # Return Register Form
    return render_template("parts/login-register.html")


@app.route('/q/register', methods=['POST'])
def register():
    # Register User
    name = request.form['username']
    query = user.User.select().where(user.User.username == name)
    if query:
        # If User exists, abort! They can login.
        return abort(403)
    password = request.form['password']
    # We create the user with a sesskey; a unique identifier that is used to identify the user
    # in the registration process from here on out
    query = user.User.create(username=name, password=password, sesskey=str(uuid.uuid4()))
    if query:
        # We return the next part of the registration process with the user, and all available
        # classes to choose from
        classes = cclass.CharacterClass.select().where(cclass.CharacterClass.primary == True)
        return render_template("parts/login-character.html", user=query, classes=classes), 201
    return abort(500)


@app.route('/q/registerfin', methods=['POST'])
def register_fin():
    # Complete Registration of User
    try:
        # Let's try to save the User
        query = user.User.get(user.User.pid == request.form['user'])
        if query.sesskey == request.form['sesskey']:
            query.character = request.form['name']
            query.cclass = cclass.CharacterClass.get(cclass.CharacterClass.pid == request.form['cclass'])
            query.sesskey = str(uuid.uuid4())
            query.save()

            # Alright we're good! Let's login!
            session['userid'] = query.pid
            session['sesskey'] = query.sesskey
            return '', 200
        else:
            raise ValueError("Invalid Sesskey")
    except Exception as e:
        print(e)
        return abort(500)


@app.route('/q/start')
def start():
    if not player().logs:
        return jsonify(**element().json(player()))
    return jsonify(**player().json_logs(element()))


@app.route('/q/menu')
def menu():
    return render_template("layouts/%s.html" % request.args.get("menu"), player=player(),
                           element=element(), location=location())


def story_jsonify(p, result):
    if isinstance(result, story.StoryAdvancement):
        p.gamemajor = result.major
        p.gameminor = result.minor
        p.gamestate = result.state
        p.gameargs = result.args
        p.save()
        return jsonify(**element().json(p, result.commands))
    elif isinstance(result, story.StoryPass):
        return jsonify(**result.json(p))
    print(result)
    return abort(400)


@app.route('/q/act', methods=['POST'])
def act():
    if 'value' not in request.form or len(request.form['value']) == 0:
        return abort(401)
    action = request.form['value'].split("-")
    print(action)
    p = player()
    if action[0] == 'r':
        result = element().respond(p, action[1])
    elif action[0] == 'l' and action[1] == 'look':
        output = location().look(p)
        result = element().execute(p, action[1], output)
    elif action[0] == 'l' and action[1] == 'examine':
        output = location().examine(p, action[2])
        result = element().execute(p, action[1], output)
    elif action[0] == 'l' and action[1] == 'pickup':
        output = location().pickup(p, action[2])
        result = element().execute(p, action[1], output)
    else:
        result = element().execute(p, action[1])
    return story_jsonify(p, result)


@app.route('/q/localeact')
def localeact():
    return jsonify(**{"actions": location().actions(player())})


@app.route('/q/localetravel')
def localetravel():
    l = location()
    linked = [{"value": l.key, "name": l.name}]
    for link in l.linked:
        linked.append({"value": link.key, "name": link.name})
    return jsonify(**{"linked": linked})


@app.route('/q/travel')
def travel():
    key = request.args.get("key")
    prev = location().key
    if key != prev:
        p = player()
        p.location = key
        p.save()
        result = element().execute(p, 'travel', location().travel_str(prev))
        return story_jsonify(p, result)
    return '', 200


@app.route('/q/startcombat')
def start_combat():
    p = player()
    e = element()
    combat = Combat(p, e.combat(p))
    if isinstance(e, tutorial.Tutorial):
        combat.tutorial = True
    gstory.combat[p.sesskey] = combat
    return render_template("layouts/combat.html", player=p, element=element(), location=location(),
                           combat=combat)


@app.route('/q/combatact', methods=['POST'])
def combatact():
    p = player()
    c = gstory.combat[p.sesskey]
    print(request.form)
    return jsonify(**{"commands": c.act_turn(request.form)})


@app.route('/q/pequip', methods=['POST'])
def pequip():
    args = request.form['skill'].split('-')
    result = player().equip(args[2], args[3])
    if result:
        return '', 200
    return abort(500)


@app.route('/q/punequip', methods=['POST'])
def punequip():
    args = request.form['skill'].split('-')
    result = player().unequip(args[2])
    if result:
        return '', 200
    return abort(500)

# This code starts the server.
# The __main__ check means it only runs if this file is the entry point of the program.
if __name__ == '__main__':
    app.debug = True
    app.secret_key = str(uuid.uuid4())
    app.run()
else:
    app.secret_key = str(uuid.uuid4())