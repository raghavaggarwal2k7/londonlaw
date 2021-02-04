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


from twisted.python import log
import shelve, os, time, configparser, gettext
from londonlaw.common.protocol import *
from londonlaw.common import util


# mark translatable strings for xgettext
def N_(arg):
   return arg

class PasswordError(Exception):
   def ustr(self):
      return self.args[0]

class UserError(Exception):
   def ustr(self):
      return self.args[0]


# Don't instantiate directly, unless you want to also handle
# the exception.  Use getHandle().
#
# The game registry tracks four items:
#   * self._games is a dict of open games, keyed by game room name
#   * self._users is a dict that maps username to (password, last IP address)
#   * self._clients is a dict that maps username to protocol instance
#   * self._unjoinedUsers is a Set of player usernames that are not
#     currently joined to a game
#
# self._games and self._users are persistent structures stored via the
# 'shelve' module.
#
# Avoid trying to access the dictionaries directly.  Since module 'shelve'
# permits only strings as dictionary keys, there is some UTF-8
# encoding/decoding going on under the hood.

registry = None

class GameRegistrySingleton:
   def __init__(self, dbDir):
      dbDir = os.path.normpath(dbDir)
      if not os.path.isdir(dbDir):
         os.makedirs(dbDir)

      # read and parse server configuration file
      configParser   = configparser.SafeConfigParser()
      configFilename = os.path.join(dbDir, "config")
      self._adminPassword  = None
      self._expiration     = None
      if os.path.exists(configFilename):
         f = open(configFilename)
         configParser.readfp(f)
         if configParser.has_option("server", "admin_password"):
            self._adminPassword = configParser.get("server", "admin_password")
         if configParser.has_option("server", "game_expiration"):
            self._expiration = configParser.getint("server", "game_expiration")
         f.close()

      # load in the game and user databases
      self._games = shelve.open(os.path.join(dbDir, "games_db." + LLAW_VERSION), 
            "c", writeback = True)
      self._users = shelve.open(os.path.join(dbDir, "users_db." + LLAW_VERSION), 
            "c", writeback = True)
      self._clients       = {}
      self._unjoinedUsers = set()


   def addClient(self, client):
      self._clients[client.getUsername()] = client

   def addGame(self, game):
      if game.getName() not in self._games:
         self._games[game.getName()] = game
      else:
         raise Exception(N_("Game name in use."))

   def addUnjoinedUser(self, username):
#      print("add user="+username)
      self._unjoinedUsers.add(username)

   def close(self):
      log.msg(util.printable(_("Closing game registry")))
      self._games.close()
      self._users.close()

   def deleteUser(self, username):
      del self._users[username]

   def getClient(self, username):
      return self._clients[username]

   def getConnectedUserList(self):
      return list(self._clients.keys())

   def getGame(self, gameName):
      return self._games[gameName]

   def getGameList(self):
      return list(self._games.values())

   def getLastAddress(self, username):
      return self._users[username][1]

   def getPassword(self, username):
      if username == "admin":
         return self._adminPassword
      else:
         return self._users[username][0]

   def getUnjoinedUsers(self):
      return self._unjoinedUsers

   def getUserList(self):
      users = list(self._users.keys())
#      decoded = [u.decode("utf-8") for u in users]
      decoded = [u for u in users]
      decoded.sort()
      return decoded

   def hasGame(self, gameName):
      return gameName in self._games

   def purgeBotGames(self):
      # purge any games that have bots
      log.msg(util.printable(_("Purging games involving AI clients")))
      games = list(self._games.values())
      for game in games:
         for player in game.getPlayers():
            if player[-5:] == '[bot]':
               self.purgeGame(game)
               break

   def purgeExpiredGames(self):
#      if self._expiration > 0:
      if self._expiration != None:
         log.msg(util.printable(_("Purging expired games")))
         games = list(self._games.values())
         for game in games:
            if (time.time() - game._startTime) / 3600 > self._expiration:
               self.purgeGame(game)

   def purgeGame(self, game):
      if game.getName() in self._games:
         playerList = game.getPlayers()[:]
         playerConnected = False 
         for player in playerList:
            if player in self._clients:
               playerConnected = True
               break
         if not playerConnected:
            for player in playerList:
               game.removePlayer(player, force_remove=True)
            self.removeGame(game)
            for p in self.getUnjoinedUsers():
               self.getClient(p).sendUntagged("gameremoved", game.getName())

   def registerUser(self, username, password, address):
      if username == "admin":
         if self._adminPassword == None:
            raise PasswordError(N_("admin login disabled.  Consult the user manual to enable administrator access."))
         elif password != self._adminPassword:
            raise PasswordError(N_("Incorrect password."))
      elif username not in self._users:
         self._users[username] = (password, address)
      else:
         if username in self._clients:
            raise UserError(N_("That username is in use."))
         elif password != self._users[username][0]:
            raise PasswordError(N_("Incorrect password."))
         else:
            self._users[username] = (password, address)

   def removeClient(self, client):
      if client.getUsername() in self._clients:
         del self._clients[client.getUsername()]

   def removeGame(self, game):
      if game.getName() in self._games:
         del self._games[game.getName()]
         log.msg(util.printable(_("Removed game \"%(gamename)s\"") % 
            {"gamename": game.getName()}))

   def removeUnjoinedUser(self, username):
      try:
         self._unjoinedUsers.remove(username)
      except KeyError:
         pass

   def removePassword(self, username):
      (oldPass, oldIP) = self._users[username]
      self._users[username] = (None, oldIP)

   def setPassword(self, username, password):
      (oldPass, oldIP) = self._users[username]
      self._users[username] = (password, oldIP)

   def unRegisterUser(self, username):
      if username in self._users:
         del self._users[username]

def getHandle(dbDir):
   global registry
   
   if registry == None:
      registry = GameRegistrySingleton(dbDir)
   return registry