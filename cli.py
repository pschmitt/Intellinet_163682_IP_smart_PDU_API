#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import logging
import os
import re
import sys
import time
from api import IPU


LOGGER = logging.getLogger("pdu.cli")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H", "-s", "--hostname", default=os.environ.get("PDU_HOSTNAME")
    )
    parser.add_argument(
        "-u", "--username", default=os.environ.get("PDU_USERNAME")
    )
    parser.add_argument(
        "-p", "--password", default=os.environ.get("PDU_PASSWORD")
    )
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    parser.add_argument(
        "ACTION", help="Action to perform: on|off|states|status"
    )
    parser.add_argument("OUTLETS", nargs="*")
    return parser.parse_args()


def get_outlet_states(pdu):
    states = pdu.status().get("outlet_states")
    outlets = {int(_id[-1]): name for (_id, name) in pdu.outlet_names()}
    output = {}
    for o_id, outlet in outlets.items():
        output[outlet] = {"id": int(o_id), "state": states[o_id]}
    return output


def get_outlet_id(pdu, name):
    states = get_outlet_states(pdu)
    for outlet_name, outlet_data in states.items():
        if name == outlet_name:
            return outlet_data.get("id")


def get_outlet_ids(pdu, outlets):
    if not isinstance(outlets, list):
        outlets = [outlets]
    outlet_ids = []
    states = get_outlet_states(pdu)
    for o in outlets:
        if isinstance(o, int) or re.match(r"\d+", o):
            outlet_ids.append(o)
        else:
            for name, data in states.items():
                if name == o:
                    outlet_ids.append(data.get("id"))
    return sorted(set([int(x) for x in outlet_ids]))


def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        LOGGER.debug(f"ARGS: {args}")

    pdu = IPU(args.hostname, auth=(args.username, args.password))

    outlet_ids = get_outlet_ids(pdu, args.OUTLETS) if args.OUTLETS else None
    if args.debug:
        LOGGER.debug(f"Outlet IDS: {outlet_ids}")

    if args.ACTION in ["toggle", "t"]:
        LOGGER.debug(f"Toggling outlets {outlet_ids}")
        pdu.disable_outlets(outlet_ids)
        time.sleep(1)
        pdu.enable_outlets(outlet_ids)
    elif args.ACTION in ["on", "o", "enable", "e"]:
        LOGGER.debug(f"Enabling outlets {outlet_ids}")
        pdu.enable_outlets(outlet_ids)
    elif args.ACTION in ["off", "f", "disable", "d"]:
        LOGGER.debug(f"Disabling outlets {outlet_ids}")
        pdu.disable_outlets(outlet_ids)
    elif args.ACTION in ["states"]:
        output = get_outlet_states(pdu)
        print(json.dumps(output, indent=2))
    elif args.ACTION in ["status", "st", "s"]:
        print(json.dumps(pdu.status(), indent=2))
    else:
        print(f"Unknown action: {args.ACTION}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
