#Temperature Administrator
Version 1.0


[![Coverage Status](https://coveralls.io/repos/Teddy-Schmitz/temperature_admin/badge.svg?branch=master&service=github)](https://coveralls.io/github/Teddy-Schmitz/temperature_admin?branch=master)


[![Build Status](https://travis-ci.org/Teddy-Schmitz/temperature_admin.svg?branch=master)](https://travis-ci.org/Teddy-Schmitz/temperature_admin)
###Overview

A control panel to view the temperature and humidity of a location as well as the ability to control an A/C unit.  Generally the data as well as the ability to control is provided by an Arduino with a sensor and iR system but can be any system that supports json or http requests.

## Requirements

- Python 2.7

Doesn't work in Python 3 due to gevent-socketio but I'll be looking to port it over once that is compatible.

- Arduino or other temperature sensor

The main requirement is that your temperature sensor either has a REST API that the application can hit or can hit the application on its REST API.

## Setup

git clone this repository

install requirements (better to do so in a virtualenv)

`pip install -r requirements.txt`

create database using any of the SQLAlchemy compatible database

copy config-template.py to config.py and edit according to your environment

`cp config-template.py config.py`

Setup the database

`python run.py db setup`

Start the server, you'll probably want to run this in a screen/tmux session.

`python run.py runserver`

The initial admin user/password is

admin
admin123

I recommend changing this immediately on the user page.


### Configuration

These are configuration items specific to the application itself.  Check [here](http://flask.pocoo.org/docs/0.10/config/#configuration-basics) for flask configuration items.


<table>
<tr>
    <td>Option</td>
    <td>Description</td>
</tr>
<tr>
    <td>SCHEDULER</td>
    <td>Whether to run tasks defined in task.py. Default: True</td>
</tr>
<tr>
    <td>ARDUINO_IP</td>
    <td>IP or hostname of the device to check for temperature/humidity information.</td>
</tr>
<tr>
    <td>SERVER_IP</td>
    <td>The IP the server listens on. Default: 127.0.0.1</td>
</tr>
<tr>
    <td>SERVER_PORT</td>
    <td>The port the server listens on. Default: 5000</td>
</tr>
</table>


### Upgrades

If there are database schema changes you will need to run

```python run.py db upgrade```

after downloading the latest code.


### Arduino sketch

You can find the arduino sketch I'm using with this application [here](link later).