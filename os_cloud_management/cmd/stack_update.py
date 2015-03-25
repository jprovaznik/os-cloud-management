# Copyright 2015 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import logging
import textwrap

from os_cloud_management.cmd.utils import _clients as clients
from os_cloud_management.cmd.utils import environment
from os_cloud_management import updates


def parse_args():
    description = textwrap.dedent("""
    Run stack update.
    """)

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-s', '--stack', dest='orig_stack',
                        help='Name or ID of a stack to update')
    parser.add_argument('-c', '--continue', dest='update_stack',
                        help='Name or ID of a stack representing an '
                        'existing update')
    parser.add_argument('-t', '--template', dest='template',
                        help='A template containing UpdateConfig to be '
                        'used for update')
    parser.add_argument('-n', '--name', dest='update_name',
                        help='Name for the update stack')
    parser.add_argument('-i', '--interactive', dest='interactive',
                        action='store_true',
                        help='Run update process in interactive mode')
    environment._add_logging_arguments(parser)
    return parser.parse_args()


def main():
    args = parse_args()
    environment._configure_logging(args)
    try:
        environment._ensure()
        client = clients.get_heat_client()
        if args.orig_stack:
            update = updates.UpdateManager(client=client)
            update.start(args.orig_stack, args.template, args.update_name)
        elif args.update_stack:
            update = updates.UpdateManager(client=client,
                                           stack_id=args.update_stack)
        if args.interactive:
            update.do_interactive_update()
        else:
            print("status: {0} ({1})".format(update.get_status()))
    except Exception:
        logging.exception("Unexpected error during command execution")
        return 1
    return 0
