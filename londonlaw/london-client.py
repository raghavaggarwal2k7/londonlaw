#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004 Paul Pelzl
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License, Version 2, as 
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import gettext, sys, os
import locale

try:
    import guiclient
#    cwd = os.path.split(os.path.abspath(os.getcwd()))
    cwd=os.getcwd()
#    print("Pfad="+cwd+"\n")
    print(os.environ['LANGUAGE'])
    trans = gettext.translation("londonlaw", cwd+"/londonlaw/locale", [os.environ['LANGUAGE']])
    trans.install()
#    gettext.install("londonlaw",cwd+"/londonlaw/locale") # use system locale dir if client was installed
#    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    encoding=locale.getdefaultlocale()
    print ("encoding: "+format(encoding)+"," )    
    print (_("Attempting to launch client from current directory..."))
except:
    gettext.install("londonlaw", "locale") # use local locale directory if launching locally
#    print (_("Attempting to launch client from current directory...")).encode(sys.stdout.encoding, "replace")
    print (_("Attempting to launch client from current directory..."))
    import sys, os.path
    # add the parent directory to PYTHONPATH
    cwd = os.path.split(os.path.abspath(os.getcwd()))
    sys.path.append(cwd[0])
    import guiclient
    print("except")

guiclient.init()
print(_("App closed..."))

