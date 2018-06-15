#!/usr/bin/env python2

#
#  Copyright 2001 - 2016 Ludek Smid [http://www.ospace.net/]
#
#  This file is part of Outer Space.
#
#  Outer Space is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  Outer Space is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Outer Space; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import argparse
import atexit
import httplib
import json
import logging as log
import os
import re
import sys

import common as c

log.basicConfig(level=log.INFO, format='%(levelname)-7s: %(message)s')

def assertGrep(pattern, text, flags=0):
    if re.search(pattern, text, flags|re.MULTILINE):
        return True
    return False

def checkServerStatus():
    conn = httplib.HTTPConnection('localhost', '9080', timeout = 10)
    conn.request('GET', '/status')
    response = conn.getresponse()
    content = response.read()
    if response.status != 200:
        log.error("Server status not available")
        return False
    if not assertGrep('Outer Space Status Reports', content):
        log.error("Server status is malformed")
        log.debug(content)
        return False
    log.info('Server status is present.')
    return True

def checkLogs(hard=False):
    everything_ok = True
    for logfile in [c.SERVER_OUT, c.AI_OUT, c.UTILS_OUT]:
        with open(logfile.name) as readable_logfile:
            if not assertGrep('login',
                          readable_logfile.read(),
                          re.IGNORECASE):
                log.error('No valid content present in {0}'.format(logfile.name))
                everything_ok = False
                continue
        with open(logfile.name) as readable_logfile:
            if assertGrep('error|traceback',
                          readable_logfile.read(),
                          re.IGNORECASE):
                log.error('Errors present in {0}'.format(logfile.name))
                everything_ok = False
                continue
    if everything_ok:
        log.info('No error messages found in log files')
    elif hard:
        sys.exit(1)

def checkPlayerProgress():
    problem = False
    something = False
    with open(os.path.join(c.TEMP_DIR, 'website',
                           'Alpha', 'json.txt'), 'r') as stats_file:
        stats = json.loads(stats_file.read())
        buildings_counts = []
        for galaxy in stats:
            if galaxy == 'turn':
                something = True
                continue
            for player in stats[galaxy]['players']:
                player_stats = stats[galaxy]['players'][player]
                player_name = player_stats[0]
                if 'E.D.E.N.' in player_name or 'order' == player: continue
                buildings = int(player_stats[3])
                buildings_counts += [buildings]
                if buildings < 10:
                    log.error(player_stats)
                    problem = True
    if not something:
        log.error('No record in opened json')
        return False
    if problem:
        log.error('There is an issue with player progress')
        log.debug('Building counts: {0}'.format(buildings_counts))
        return False
    else:
        log.info('Player progress ok')
        return True

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--slow", dest = "slow", default = False,
    action = "store_true", help = "Switches off multiprocessing of AI")
parser.add_argument("--travis", dest = "travis", default = False,
    action = "store_true", help = "Runs limited test, suitable for Travis CI")
parser.add_argument("--turns", dest = "turns", default = 40,
    type = int, metavar = "N", help = "Process N turns on server")
parser.add_argument("--turn-skip", dest = "turnSkip", default = 5,
    type = int, metavar = "N", help = "Process N turns on server")
args = parser.parse_args()


c.initPaths()

# test itself
# check basic sanity
if not c.startServer():
    sys.exit(1)
atexit.register(c.killServer)
c.createGalaxy("Circle3BP")
c.startServerTime()
c.deleteGalaxy(10000) # legacy
c.createGalaxy("Circle42P")
c.startServerTime()
c.doTurns(args.turnSkip, args.turnSkip, slow=args.slow)
if not checkServerStatus():
    sys.exit(1)
c.stopServer()
checkLogs(hard=True)

# check upgrade sanity
if not c.startServer(upgrade=True):
    sys.exit(1)
c.doTurns(args.turnSkip, args.turnSkip, slow=args.slow)
if not checkServerStatus():
    sys.exit(1)
c.stopServer()
checkLogs(hard=True)

# this block checks player progression
if not c.startServer():
    sys.exit(1)
c.doTurns(args.turns, args.turnSkip)
if not args.travis:
    c.makeScreenshots(os.path.join(c.TEMP_DIR, 'screens'))
if not checkServerStatus():
    sys.exit(1)
c.stopServer()
if not checkPlayerProgress():
    sys.exit(1)
checkLogs(hard=True)

