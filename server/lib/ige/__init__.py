#
#  Copyright 2001 - 2016 Ludek Smid [http://www.ospace.net/]
#
#  This file is part of Outer Space.
#
#  IGE - Outer Space is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  IGE - Outer Space is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with IGE - Outer Space; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import log

## common exceptions
class SecurityException(Exception):
    pass

class GameException(Exception):
    pass

class CreatePlayerException(Exception):
    pass

class NoAccountException(Exception):
    pass

class ServerException(Exception):
    pass

class ServerStatusException(Exception):
    pass

class NoSuchObjectException(Exception):
    pass

## global settings
# runtime mode, currently supported:
#   1 - normal operations
#   0 - debug/devel operations
igeRuntimeMode = 1

def setRuntimeMode(runtimeMode):
    global igeRuntimeMode

    igeRuntimeMode = runtimeMode
    log.message("Runtime mode changed to", igeRuntimeMode)
