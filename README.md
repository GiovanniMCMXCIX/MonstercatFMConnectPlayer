# Monstercat FM Player
Monstercat FM Player is python script that gets the song that is playing on [Monstercat FM](https://www.twitch.tv/monstercat) thought Twitch IRC and uses [Monstercat Connect's API](https://www.monstercat.com/dev/api/connect) to get the audio in order to play it.

![What it looks like](https://i.imgur.com/aLqmFb9.png)

##How to use

###Before you start
- Python 3.5+ is required. The location of the Python installation must also be added to the system PATH variable.
- You will need the [connect](https://github.com/GiovanniMCMXCIX/connect.py) and the [pygame](http://www.pygame.org/download.shtml) library
- You will need an OAuth key for the account you would like to use this script with. Go to [TwitchApps](http://twitchapps.com/tmi) and connect using the account you would like to use. Keep this key in a safe place. Copy it to your clipboard - you will need it later.

###Running
- Run `start.bat` by double clicking on it. Alternatively you can run it through the Python terminal.
- It will ask you for a username. This should match the account you got an OAuth key for.
- It will ask you for the OAuth key. Copy your OAuth key, starting with "oauth:", right click and paste it. It will be hidden from sight.
- It should now connect if everything went right.
- To exit, simply close the window.

#Bugs
- sometimes the player randomly dies