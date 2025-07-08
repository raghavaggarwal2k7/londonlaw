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




# RegistrationWindow.py
#
# This module contains the classes that generate the list of players within a
# game room, permit changing teams, etc.


import os.path, gettext, wx
from twisted.python import log
import wx
from common.protocol import *
from common.config import *
from .AutoListCtrl import *
from .ChatPanel import *
from .About import *



# Create a small dialog with radio buttons, OK, and Cancel.
class RadioDialog(wx.Dialog):
   def __init__(self, parent, dialogTitle, radioTitle, options):
      wx.Dialog.__init__(self, parent, -1, dialogTitle, wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE|wx.SUNKEN_BORDER)
      panel = wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

      # TRANSLATORS: this is the label for a radiobutton group that lets the user choose a team
      self.choice = wx.RadioBox(panel, -1, radioTitle, wx.DefaultPosition, wx.DefaultSize,
          options, 1, wx.RA_SPECIFY_COLS)
      self.submitButton = wx.Button(panel, wx.ID_OK, _("OK"))
      self.cancelButton = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))

      buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
      buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      buttonSizer.Add(self.submitButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

      vSizer = wx.BoxSizer(wx.VERTICAL)
      vSizer.Add(self.choice, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      vSizer.Add((1, 1), 1, wx.EXPAND)
      vSizer.Add(buttonSizer, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

      panel.SetSizer(vSizer)
      vSizer.Fit(panel)
      sizer = wx.BoxSizer(wx.VERTICAL)
      sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
      self.SetSizer(sizer)
      sizer.Fit(self)
      self.SetAutoLayout(1)

      self.Bind(wx.EVT_BUTTON, self.submit, id=wx.ID_OK)
      self.Bind(wx.EVT_BUTTON, self.cancel, id=wx.ID_CANCEL)


   def submit(self, event):
      self.EndModal(self.choice.GetSelection())

   def cancel(self, event):
      self.EndModal(-1)



# Create a small dialog with a choice box, OK and Cancel buttons
class ChoiceDialog(wx.Dialog):
   def __init__(self, parent, dialogTitle, labelText, options):
      wx.Dialog.__init__(self, parent, -1, dialogTitle,
            wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE|wx.SUNKEN_BORDER)
      panel = wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

      self.label        = wx.StaticText(panel, -1, labelText, wx.Point(0,0))
      self.chooseBox    = wx.Choice(panel, -1, wx.DefaultPosition, wx.DefaultSize, options)
      self.submitButton = wx.Button(panel, wx.ID_OK, _("OK"))
      self.cancelButton = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))
      self.chooseBox.SetSelection(0)

      hSizer = wx.BoxSizer(wx.HORIZONTAL)
      hSizer.Add((30, 1), 0, 0)
      hSizer.Add(self.label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      hSizer.Add(self.chooseBox, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

      bSizer = wx.BoxSizer(wx.HORIZONTAL)
      bSizer.Add((1, 1), 1, 0)
      bSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      bSizer.Add(self.submitButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

      vSizer = wx.BoxSizer(wx.VERTICAL)
      vSizer.Add(hSizer, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      vSizer.Add(bSizer, 0, wx.EXPAND|wx.ALL, 5)

      panel.SetSizer(vSizer)
      vSizer.Fit(panel)
      sizer = wx.BoxSizer(wx.VERTICAL)
      sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
      self.SetSizer(sizer)
      sizer.Fit(self)
      self.SetAutoLayout(1)

      self.Bind(wx.EVT_BUTTON, self.submit, id=wx.ID_OK)
      self.Bind(wx.EVT_BUTTON, self.cancel, id=wx.ID_CANCEL)


   def submit(self, event):
      self.EndModal(self.chooseBox.GetSelection())

   def cancel(self, event):
      self.EndModal(-1)



# Generate the main registration window.
class RegistrationWindow(wx.Frame):
   def __init__(self, parent, ID, title, messenger, exitCallback):
      title=title+" - "+messenger.getGamename()   
      wx.Frame.__init__(self, parent, ID, title)

      self.exitCallback = exitCallback
      self._messenger   = messenger

      DISCONNECT = 100
      EXIT       = 101
      ABOUTWIN   = 102

      # Create a menu bar
      # TRANSLATORS: this is a menu bar entry
      fileMenu = wx.Menu()
      # TRANSLATORS: this is a menu bar entry
      fileMenu.Append(DISCONNECT, _("Disconnect"), _("Disconnect from server"))
      # TRANSLATORS: this is a menu bar entry
      fileMenu.Append(EXIT, _("Exit%(hotkey)s") % {"hotkey" : "\tCTRL+Q"}, _("Exit London Law"))

      helpMenu = wx.Menu()
      helpMenu.Append(ABOUTWIN, _("About%(hotkey)s") % {"hotkey" : "\tCTRL+A"}, _("About"))

      menuBar = wx.MenuBar()
      # TRANSLATORS: this is a menu bar entry
      menuBar.Append(fileMenu, _("File"))
      menuBar.Append(helpMenu, _("Help"))
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar()

      # stick everything in a panel
      mainPanel = wx.Panel(self, -1)

      self.list = AutoListCtrl(mainPanel, -1,
            # TRANSLATORS: these are column labels for the window where the players choose teams for a game
            (_("Player"), 
            # TRANSLATORS: these are column labels for the window where the players choose teams for a game
               _("Team"), 
            # TRANSLATORS: these are column labels for the window where the players choose teams for a game
               _("Votes to Start?"), 
            # TRANSLATORS: these are column labels for the window where the players choose teams for a game
               _("Pawns")),
            # TRANSLATORS: this is displayed in a column when no players have joined one of the games
            (_("(no players joined)"), "", "", ""))

      self.list.SetColumnWidth(1, 140) 

      mainSizer = wx.BoxSizer(wx.VERTICAL)
      mainSizer.Add(self.list, 3, wx.ALIGN_CENTRE|wx.ALL, 5)

      self.chatWindow = ChatPanel(mainPanel, "", False)
      mainSizer.Add(self.chatWindow, 2, wx.EXPAND|wx.ALL, 5)

      self.leaveButton = wx.Button(mainPanel, -1, _("Leave Game"))
      self.teamButton  = wx.Button(mainPanel, -1, _("Choose Team"))
      self.voteButton  = wx.Button(mainPanel, -1, _("Vote to Start"))
      buttonSizer      = wx.BoxSizer(wx.HORIZONTAL)
      buttonSizer.Add(self.leaveButton, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALL, 5)
      buttonSizer.Add((1, 1), 1, wx.EXPAND)
      buttonSizer.Add(self.teamButton, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.BOTTOM | wx.ALL, 5)
      buttonSizer.Add(self.voteButton, 0, wx.ALIGN_CENTRE | wx.RIGHT | wx.BOTTOM | wx.ALL, 5)
      mainSizer.Add(buttonSizer, 0, wx.EXPAND, 0)

      mainPanel.SetSizer(mainSizer)
      mainSizer.Fit(mainPanel)

      self.Bind(wx.EVT_CLOSE, self.menuExit)
      self.Bind(wx.EVT_MENU, self.menuExit, id=EXIT)
      self.Bind(wx.EVT_MENU, self.menuDisconnect, id=DISCONNECT)
      self.Bind(wx.EVT_BUTTON, self.leaveGame, id=self.leaveButton.GetId()) 
#      self.Bind(wx.EVT_BUTTON, self.requestAIList, id=self.aiButton.GetId())
      self.Bind(wx.EVT_BUTTON, self.chooseTeam, id=self.teamButton.GetId())
      self.Bind(wx.EVT_BUTTON, self.voteStart, id=self.voteButton.GetId())
      self.Bind(wx.EVT_TEXT_ENTER, self.chatSend, id=self.chatWindow.chatEntry.GetId())
      self.Bind(wx.EVT_MENU, self.showAbout, id=ABOUTWIN)

   # display the About dialog
   def showAbout(self, event):
      AboutWindow.showAbout(self)   	 


   def addPlayer(self, data):
      print("addplayer")   	
      log.msg("called RegistrationWindow.addPlayer()")
      self.list.addItem(data)


   def removePlayer(self, data):
      log.msg("called RegistrationWindow.removePlayer()")
      self.list.removeItemByData(data)


   def addChatMessage(self, chatType, data):
      log.msg("called RegistrationWindow.addChatMessage()")
      self.chatWindow.AppendText("<" + data[0] + "> " + self.chatWindow.remove_quotes(data[1][1:]))
      print("<" + data[0] + "> " + self.chatWindow.remove_quotes(data[1][1:]))  # For debugging purposes, print to console


   def chatSend(self, event):
      (text, sendTo) = self.chatWindow.GetEntry()
      if len(text) > 0:
         self.chatWindow.ClearEntry()
         self._messenger.netSendChat(text, sendTo)


   def enableSelectButton(self, event):
      self.selectButton.Enable(True)


   def disableSelectButton(self, event):
      self.selectButton.Disable()

      
   def disableVoteButton(self):
      self.voteButton.Disable()


   def chooseTeam(self, event):
      teamDialog = RadioDialog(self, _("Choose a Team"),
      # TRANSLATORS: this is the label for a radiobutton group that lets the user choose a team
         _("team: "),
      # TRANSLATORS: this is one of the two team names
         [_("Detectives"), 
      # TRANSLATORS: this is one of the two team names
          _("Mr. X")])
      value = teamDialog.ShowModal()  # 0 == Detectives, 1 == Mr. X
      if value == 0:
         self._messenger.netSetTeam("Detectives")
      elif value == 1:
         self._messenger.netSetTeam("Mr. X")


   def requestAIList(self, event):
      teamDialog = RadioDialog(self, _("Choose a Team"),
         _("AI opponent's team: "),
      # TRANSLATORS: this is one of the two team names
         [_("Detectives"), 
      # TRANSLATORS: this is one of the two team names
          _("Mr. X")])
      value = teamDialog.ShowModal()  # 0 == Detectives, 1 == Mr. X
      if value == 0:
         self._messenger.netRequestAIList("Detectives")
      elif value == 1:
         self._messenger.netRequestAIList("Mr. X")


   def leaveGame(self, event):
      self._messenger.netLeaveGame()


   def selectAI(self, algorithms):
      aiDialog = ChoiceDialog(self, _("Choose an AI Algorithm"),
         _("AI algorithm: "), algorithms)
      value = aiDialog.ShowModal()  # 0 == Detectives, 1 == Mr. X
      if value != -1:
         self._messenger.netRequestAI(algorithms[value])


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = wx.MessageDialog(self, info,
         # TRANSLATORS: this is the title for a small alert window that pops up when the server reports an error
         _("Server Message"), wx.OK|wx.ICON_INFORMATION)
      alert.ShowModal()


   def voteStart(self, event):
      self._messenger.netVoteStart()


   def menuExit(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server and exit London Law?"),
         _("Disconnect and Quit"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self._messenger.netShutdown()
         self.exitCallback(self)
         self.Destroy()


   def menuDisconnect(self, event):
      alert = wx.MessageDialog(self, _("Disconnect from the server?"),
         _("Disconnect"), wx.YES_NO|wx.ICON_EXCLAMATION)
      if alert.ShowModal() == wx.ID_YES:
         self._messenger.netDisconnect()

      



