#  XCanasta -- Network-compatible computer variant of the popular card game
#  Copyright (C) 2021 Horst Aldebaran
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

import sys, gettext, wx
import os, wx.adv
from common.protocol import *


# Initial window.  AboutWindow
class AboutWindow(wx.Frame):

   def showAbout(self):
      cwd=os.getcwd()
      ABOUT_ICON = cwd+"/londonlaw/guiclient/images/about.jpg"
      info = wx.adv.AboutDialogInfo()
      info.Name = "Londonlaw"
      info.SetIcon (wx.Icon(ABOUT_ICON, wx.BITMAP_TYPE_JPEG))        
      info.Version = LLAW_VERSION
      info.Copyright = '(C) GPL-2.0 Licence'
      info.Description = "A multiplayer manhunting adventure by Paul Pelzl\n modified by Horst Aldebaran"
      info.SetWebSite('https://github.com/horald/londonlaw')
      info.Developers = [ 'Paul Pelzl, Horst Aldebaran']
      info.AddTranslator('Horst Meyer')

      # Then we call wx.AboutBox giving it that info object
      wx.adv.AboutBox(info)    	

