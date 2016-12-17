#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Argos.
#
# Argos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Argos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Argos.  If not, see <http://www.gnu.org/licenses/>.

""" Argos numerical data inspector.
"""
from __future__ import print_function

import logging, sys, argparse
logger = logging.getLogger('libargos')
logging.basicConfig(level='DEBUG', stream=sys.stderr,
                    format='%(asctime)s %(filename)25s:%(lineno)-4d : %(levelname)-7s: %(message)s')

from libargos import browse
from libargos.application import printInspectors
from libargos.qt.misc import ABOUT_QT_BINDINGS
from libargos.info import DEBUGGING, PROJECT_NAME, VERSION, DEFAULT_PROFILE
from libargos.utils.misc import remove_process_serial_number


def main():
    """ Starts Argos main window
    """
    about_str = "{} version: {}".format(PROJECT_NAME, VERSION)
    parser = argparse.ArgumentParser(description = about_str)

    parser.add_argument('fileNames', metavar='FILE', nargs='*', help='Input files')

    parser.add_argument('-i', '--inspector', dest='inspector',
        help="""The identifier or fullName of the inspector that will be opened at start up.
                E.g. 'Qt/Table'""")

    parser.add_argument('--list-inspectors', dest='list_inspectors', action = 'store_true',
        help="""Prints a list of available inspectors for the -i option""")


    parser.add_argument('-s', '--select', dest='selectPath',
        help="""Full path name of a repository tree item that will be selected at start-up.
                E.g. 'file/var/fieldname'""")

    parser.add_argument('-p', '--profile', dest='profile', default=DEFAULT_PROFILE,
        help="Can be used to have different persistent settings for different use cases.")

    parser.add_argument('--reset', '--reset-profile', dest='reset_profile', action = 'store_true',
        help="If set, persistent settings will be reset for the current profile.")

    parser.add_argument('--reset-all-profiles', dest='reset_all_profiles', action = 'store_true',
        help="If set, persistent settings will be reset for the all profiles.")

    parser.add_argument('--reset-registry', dest='reset_registry', action = 'store_true',
        help="If set, the registry will be reset to contain only the default plugins.")

    parser.add_argument('--version', action = 'store_true',
        help="Prints the program version.")

    parser.add_argument('-L', '--log-level', dest='log_level', default='warn',
        help="Log level. Only log messages with a level higher or equal than this will be printed."
        "Default: 'warn'", choices=('debug', 'info', 'warn', 'error', 'critical'))

    args = parser.parse_args(remove_process_serial_number(sys.argv[1:]))

    logger.info("Setting log level to: {}".format(args.log_level.upper()))
    logger.setLevel(args.log_level.upper())

    logger.info('Started {} {}'.format(PROJECT_NAME, VERSION))
    logger.info("Python version: {}".format(sys.version).replace('\n', ''))
    #logger.info('Using: {}'.format('PyQt' if USE_PYQT else 'PySide'))
    logger.info("Using {}".format(ABOUT_QT_BINDINGS))

    if DEBUGGING:
        logger.warn("Debugging flag is on!")

    if args.version:
        print(about_str)
        sys.exit(0)

    if args.list_inspectors:
        printInspectors()
        sys.exit(0)

    # Browse will create an ArgosApplication with one MainWindow
    browse(fileNames = args.fileNames,
           inspectorFullName=args.inspector,
           select=args.selectPath,
           profile=args.profile,
           resetProfile=args.reset_profile,
           resetAllProfiles=args.reset_all_profiles,
           resetRegistry=args.reset_registry)
    logger.info('Done {}'.format(PROJECT_NAME))

if __name__ == "__main__":
    main()