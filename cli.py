#!/usr/bin/env python
# coding: utf-8

import argparse
import json
import os
import time
from api import IPU


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
    parser.add_argument("ACTION")
    parser.add_argument("OUTLETS", nargs="*")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        print(args)
    pdu = IPU(args.hostname, auth=(args.username, args.password))
    if args.ACTION in ["toggle", "t"]:
        pdu.disable_outlets(args.OUTLETS)
        time.sleep(1)
        pdu.enable_outlets(args.OUTLETS)
    elif args.ACTION in ["on", "o", "enable", "e"]:
        pdu.enable_outlets(args.OUTLETS)
    elif args.ACTION in ["off", "f", "disable", "d"]:
        pdu.disable_outlets(args.OUTLETS)
    elif args.ACTION in ["states"]:
        states = pdu.status().get("outlet_states")
        outlets = {int(_id[-1]): name for (_id, name) in pdu.outlet_names()}
        for o_id, outlet in outlets.items():
            print(f"{outlet}: {states[o_id]}")

    elif args.ACTION in ["state", "status", "st", "s"]:
        print(json.dumps(pdu.status()))


if __name__ == "__main__":
    main()
