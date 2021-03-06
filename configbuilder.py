#!/usr/bin/env python
from __future__ import print_function
import json
import os
import fnmatch
import pytz
import sys

if sys.version[0] == '3':
    raw_input = input

# Hardcoded sections
usersource = {
    "host": "https://callook.info",
    "username": None
}

satsource = {
    "celestrak": {
        "path": None,
        "host": "www.celestrak.com",
        "filename": {
            "noaa": "noaa.txt",
            "weather": "weather.txt",
            "amateur": "amateur.txt",
            "ham": "amateur.txt",
            "wx": "weather.txt"
        }
    },
    "amsat": {
        "path": "amsat/ftp/keps/current",
        "host": "www.amsat.org",
        "filename": {
            "ham": "nasabare.txt"
        }
    }
}


def find_db():
    """Search the directory tree and return and files named *.db"""
    matches = []
    pattern = '*.db'

    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                matches.append(os.path.join(root, name))
    return matches


def get_db_name():
    """Generates the datasource section of the config file.
    sqlite3 is the only type supported"""
    available_dbs = find_db()
    total_dbs = len(available_dbs)
    if total_dbs == 0:
        db_name = raw_input('Enter name for database: ')
        existing = False
    else:
        print('Multiple Databases found')
        for idx, db_name in enumerate(available_dbs):
            print('\t{} - {}'.format(idx, db_name))
        print('\tN - New Database')
        db_index = raw_input('Which database do you want to use? ')
        if db_index.upper() == 'N':
            db_name = raw_input('Enter name for database: ')
            existing = False
        else:
            try:
                db_index = int(db_index)
                try:
                    db_name = available_dbs[db_index]
                    existing = True
                except IndexError:
                    print('That is not a valid DB')
                    get_db_name()
            except ValueError:
                print('Invalid entry, Valid values are integers or \'N\' for a new db')
                get_db_name()
    return {'type': 'sqlite3',
            'filename': '../{}'.format(db_name.split('/')[-1]),
            'Username': None,
            'Password': None,
            'Existing': existing}


def get_callinfo():
    callsign = raw_input('Enter Callsign: ')
    userzone = raw_input('Enter Timezone: ')
    try:
        pytz.timezone(userzone)
    except pytz.UnknownTimeZoneError as err:
        print('Invalid Timezone entered.\n {}'.format(err))
        userzone = raw_input('Enter Timezone: ')
    return {'callsign': callsign.upper(),
            'timezone': userzone
            }


def write_db_file(config_dict):
    destination_file = 'config/config.json'
    if os.path.isfile(destination_file):
        overwrite = raw_input('File already exists, rewrite? (y/n): ')
        if overwrite.upper() == 'Y':
            new_filename = '{}.renamed'.format(destination_file)
            os.rename(destination_file, new_filename)
        else:
            print('Existing file not overwritten, Exiting')
            sys.exit()
    with open(destination_file, 'w') as config_file:
        config_file.write(json.dumps(config_dict, indent=2))


def get_age_threshold():
    tle_age = int(raw_input('Max age of tle files (days)? '))
    qth_data = int(raw_input('Time before retreiving new QTH data (days)? '))
    return {"tle_file": tle_age,
            "qth_data": qth_data}


datasource = get_db_name()
default_location = get_callinfo()
age_threshold = get_age_threshold()

config_object = {'name': 'blah',
                 'age_thresholds': age_threshold,
                 'default_location': default_location,
                 'datasource': datasource,
                 'satsource': satsource,
                 'usersource': usersource,
                 }
write_db_file(config_object)
