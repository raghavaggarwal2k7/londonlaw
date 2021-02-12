
London Law
----------

<b>The game still has some bugs, but it can be played now!</b>

London Law is an online multiplayer adaptation of the [classic Scotland Yard
board game](http://www.boardgamegeek.com/boardgame/438/scotland-yard)
([Wikipedia](http://en.wikipedia.org/wiki/Scotland_Yard_board_game)).

This repository is based on a copy of the [last known pre-release](http://www.freelists.org/post/londonlaw-users/030-preview-release)
(0.3pre1) of [London Law](http://pessimization.com/software/londonlaw/) released
by the original author Paul Pelzl and contains additional patches to make this
game work with modern software.

Please note: I will not invest much time into development but patches are welcome.

Screenshot:
-----------

[![Screenshot](http://anyc.github.io/londonlaw/images/screenshot_thumb.jpg)](http://anyc.github.io/londonlaw/images/screenshot.jpg)

Dependencies:
-------------
* Python
* [Twisted](https://twistedmatrix.com)
* [wxPython](http://www.wxpython.org/)

The code has been tested with the following versions:
* Python 3.8.5
* Twisted-18.9.0
* wxPython-4.0.7

get started:
------------

<h3>For Ubuntu</h3>
<code>sudo apt install python3-wxgtk4.0</code> (only for the client)<br>
<code>sudo apt install python3-twisted</code>

* Run Server:<br>
  python3 londonlaw/london-server.py

* Run Client:<br>
  python3 londonlaw/london-client.py [ip-adress] [player] [password] [gamename]<br>
  (The parameters are optional.)

<h3>For Windows</h3>
Check, if you have Python3 installed:<br>
<code>python --version</code><br>
Python 3.8.5

Install the libraries, you need administration rights:<br>
<code>pip install wxpython</code> (only for the client)<br>
<code>pip install twisted</code>

* Run Server:<br>
  python londonlaw/london-server.py

* Run Client:<br>
  python londonlaw/london-client.py [ip-adress] [player] [password] [gamename]<br>
  (The parameters are optional.)


Changes
-------

0.303:
   * ported to python3 by Horst Aldebaran alias Meyer (horald)

0.3.0pre2:

   * wxPython3.0 compatibility by Olly Betts
   * Fix for newer python-twisted by Hans de Goede
   * Accept custom data directory by Mr Bones
   * More small fixes by Mario Kicherer

[0.3.0pre1 by Paul Pelzl](http://www.freelists.org/post/londonlaw-users/030-preview-release):

   * i18n.  Thanks to the efforts of numerous translators, there is
     at least partial support for 11 different languages.
   * AI clients.  Players can request an AI opponent while registering
     for a game.  At the moment there is only a pair of "Rather Dumb"
     AI clients available, meant as a proof of concept.
   * Admin client.  There is a text-mode admin client that can be used
     to delete games, eject players, etc.  It has an online help system,
     which is hopefully enough to explain the usage.

     The admin client won't work without setting up an admin password.
     Create a file called ~/.londonlaw/server/config that looks like
     this:

         [server]
         admin_password: PASSWORD
         game_expiration: 240

     Replace PASSWORD with whatever you want.  The game expiration is
     the number of hours after which stale games should be purged.
