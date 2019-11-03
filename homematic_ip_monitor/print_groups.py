#!/usr/bin/env python3
import logging
import sys
import time
import re
from argparse import ArgumentParser
from collections import namedtuple
from logging.handlers import TimedRotatingFileHandler

import homematicip
from homematicip.device import *
from homematicip.group import *
from homematicip.rule import *
from homematicip.home import Home
from homematicip.base.helpers import handle_config



def main():
    parser = ArgumentParser(description="a cli wrapper for the homematicip API")
    parser.add_argument(
        "--config_file",
        type=str,
        help="the configuration file. If nothing is specified the script will search for it.",
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
            print("##### CONFIG FILE NOT FOUND: {} #####".format(args.config_file))
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

    sortedGroups = sorted(home.groups, key=attrgetter("groupType", "label"))
    for g in sortedGroups:
        print(g)

if __name__ == "__main__":
    main()
