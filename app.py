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
from game.model import user

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
    print(name)
    query = user.User.select().where(user.User.username == name)
    print(query)
    if query:
        return abort(403)
    password = request.form['password']
    print(password)
    query = user.User.create(username=name, password=password)
    print(query)
    if query:
        return render_template("parts/login-character.html"), 201
    return abort(500)


if __name__ == '__main__':
    app.debug = True
    app.run()
