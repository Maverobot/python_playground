#!/usr/bin/env python3
import logging
import sys
import time
import re
from argparse import ArgumentParser
from collections import namedtuple
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

import homematicip
from homematicip.device import *
from homematicip.group import *
from homematicip.rule import *
from homematicip.home import Home
from homematicip.base.helpers import handle_config


def get_current_date_and_time():
    # datetime object containing current date and time
    now = datetime.now()
    print("now =", datetime)
    # dd/mm/YY H:M:S
    return now.strftime("%d/%m/%Y %H:%M:%S")


class Data:
    def __init__(self, room_name, target_temperature, current_temperature):
        self.room_name = room_name
        self.target_temperature = target_temperature
        self.current_temperature = current_temperature

    def __str__(self):
        return "Room name: " + self.room_name + ", target temperature: " + \
            self.target_temperature + ", current temperature: " + self.current_temperature


def main():
    parser = ArgumentParser(
        description="a cli wrapper for the homematicip API")
    parser.add_argument(
        "--config_file",
        type=str,
        help=
        "the configuration file. If nothing is specified the script will search for it.",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        return
    except:
        print("could not parse arguments")
        parser.print_help()
        return

    _config = None
    if args.config_file:
        try:
            _config = homematicip.load_config_file(args.config_file)
        except FileNotFoundError:
            print("##### CONFIG FILE NOT FOUND: {} #####".format(
                args.config_file))
            return
    else:
        _config = homematicip.find_and_load_config_file()
    if _config is None:
        print("Could not find configuration file. Script will exit")
        return

    home = Home()
    home.set_auth_token(_config.auth_token)
    home.init(_config.access_point)

    if not home.get_current_state():
        print("homematicip cannot get its current state.")
        return
    print("\n")
    print("=== Homematicip Initialized ===")
    print("\n")

    rooms_map = {}

    while True:
        sortedGroups = [
            str(g)
            for g in sorted(home.groups, key=attrgetter("groupType", "label"))
        ]

        # Regex to extract (room name, target temperature, current temperature)
        regex = re.compile(
            r'HEATING (.*) window.*setPointTemperature\((\d+\.+\d*)\).*actualTemperature\((\d+\.+\d*)\)'
        )
        rooms = list(filter(regex.search, sortedGroups))

        for r in rooms:
            t = datetime.now()
            d = Data(
                regex.search(r).group(1),
                regex.search(r).group(2),
                regex.search(r).group(3))
            if d.room_name_ in rooms_map:
                rooms_map[d.room_name_].append(
                    [regex.search(r).group(2),
                     regex.search(r).group(3)])
            else:
                rooms_map[d.room_name_] = []
                rooms_map[d.room_name_].append(
                    [t, regex.search(r).group(2),
                     regex.search(r).group(3)])
        print(str(rooms_map))
        time.sleep(1)


if __name__ == "__main__":
    main()
