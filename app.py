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

from flask import Flask, abort, render_template, request
from game.model import user, cclass
import uuid

app = Flask(__name__)


@app.route('/')
def login():
    # Return Login Page
    return render_template("login.html")


@app.route('/q/logintemp')
def login_temp():
    # Return Login Form
    return render_template("parts/login-login.html")


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
    query = user.User.create(username=name, password=password, sesskey=uuid.uuid4())
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
        query.character = request.form['name']
        query.cclass = cclass.CharacterClass.get(cclass.CharacterClass.pid == request.form['class'])
        query.save()

        # Alright we're good! Let's login!
    except:
        return abort(500)


if __name__ == '__main__':
    app.debug = True
    app.run()
