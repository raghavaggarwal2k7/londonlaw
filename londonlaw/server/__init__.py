#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004, 2005 Paul Pelzl
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


from twisted.internet import protocol, reactor, task
from twisted.python import log
from common.protocol import *
from .Protocol import LLawServerProtocol
from optparse import OptionParser
from . import GameRegistry
import sys, gettext, os



class LLawServerFactory(protocol.ServerFactory):
   protocol = LLawServerProtocol
   

def init():
   # Parse command-line options
   parser = OptionParser()
   parser.add_option("-p", "--port", dest="port",
         help=_("listen for connections on port NUM"), metavar=_("NUM"), default=str(LLAW_PORT))
   parser.add_option("-a", "--addr", dest="addr",
         help=_("listen for connections on host HOST"), metavar=_("HOST"), default="127.0.0.1")
   parser.add_option("-D", "--dbdir", dest="dbdir",
         help=_("use DBDIR to store game und user database"), metavar=_("DBDIR"),
         default=os.path.expanduser("~/.londonlaw/server"))
   parser.add_option("-t", "--type", dest="type",
         help=_("listen for connections on type TCP/UDP"), metavar=_("TYPE"), default="TCP")
   (options, args) = parser.parse_args()
   
##   log.startLogging(sys.stdout, 0)
##   log.startLogging(open('./londonlaw-server.log', 'w'))
   options.dbdir=os.getcwd()+"/londonlaw/server"
   deletedb(dbDir=options.dbdir)
   registry = GameRegistry.getHandle(dbDir=options.dbdir)
   # Purge expired games every half hour
   gameKiller = task.LoopingCall(registry.purgeExpiredGames)
   loopgameKiller = gameKiller.start(1800)
   # Purge games involving AI clients
   registry.purgeBotGames()
   print("listen %s" % options.addr)   
   reactor.listenTCP(int(options.port), LLawServerFactory(), interface=options.addr)
#   reactor.listenUDP(int(options.port), LLawServerFactory(), interface="127.0.0.1")
   reactor.run()
   registry.close()

def deletedb(dbDir):
   if os.path.exists(os.path.join(dbDir, "londonlaw_games.db")): 	
      os.remove(os.path.join(dbDir, "londonlaw_games.db")) 	
   if os.path.exists(os.path.join(dbDir, "londonlaw_users.db")): 	
      os.remove(os.path.join(dbDir, "londonlaw_users.db")) 	
   	
