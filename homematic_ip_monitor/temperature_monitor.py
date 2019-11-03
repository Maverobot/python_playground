#!/usr/bin/env python3
import logging
import sys
import time
import re
from argparse import ArgumentParser
from datetime import datetime
import pandas as pd
import os

import homematicip
from homematicip.device import *
from homematicip.group import *
from homematicip.rule import *
from homematicip.home import Home
from homematicip.base.helpers import handle_config

log_file = "./temperature_log.csv"


def main():
    pd.set_option('display.width', 200)

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
    print("\n=== Homematicip Initialized ===\n")

    rooms_history = {}

    data = []
    i = 0

    # Check if the log file already exist
    if os.path.isfile(log_file):
        df = pd.read_csv(log_file)
        data = df.values.tolist()
        print(str(len(data)) + " rows have been loaded from " + log_file)
        print("")

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

        # Add new measurement into the dictionary
        t = datetime.now()
        for r in rooms:
            data.append([
                t,
                regex.search(r).group(1),
                regex.search(r).group(2),
                regex.search(r).group(3)
            ])

        # Pandas Dataframe
        data_frame = pd.DataFrame(data,
                                  columns=[
                                      "time", "room", "target_temperature",
                                      "current_temperature"
                                  ])
        data_frame.to_csv(log_file, index=False)
        print("Temperature measurement index: " + str(i))
        i = i + 1
        # Read temperature data every 10 seconds
        time.sleep(10)


if __name__ == "__main__":
    main()
