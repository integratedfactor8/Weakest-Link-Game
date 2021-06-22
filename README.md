# The Weakest Link Game
A game I made in Panda3D where you answer questions then vote off the weakest link.

# How to run it
You can run it by running the wl.py file with a Python interpreter with Panda3D installed. You need to have the assets in the correct folders, and it may not work on Windows unless you change the path in the code because Windows uses backlashes for filenames. You can install Panda3D with pip (pip install Panda3D).

# Licence
All files are licensed with the GNU Affero Public Licence 3.0 (you can see it here: https://www.gnu.org/licenses/agpl-3.0.en.html).

# Music
All music was created by me with LMMS, you can find the project files in the music/project files directory. 

# How to play
The game is based on the Weakest Link show (https://en.wikipedia.org/wiki/The_Weakest_Link_(British_game_show)), up to 9 players answer questions for a round to try and bank the most points. At the end of a round, the players will vote off the weakest link.

# First Screen
You can modify settings by clicking on the settings button, or you can start the game insantly by clicking on "Click to start." By default, the game will automatically start after the intro music is finished, you can disable that by toggling autostart with the autostart button.

# Settings
You can change some settings. You can change the number of players in total from 2 to 9 (default is 9). You can also change the number of CPUs from 0 to the total number of players (default is 8). You can also change the CPU difficulty (default is intermediate), to beginner, intermediate, advanced, expert, and master. You can also allow or disallow voting off the statistical strongest link (default is disallowed). When allowed, you can vote for anyone (but yourself), when disallowed, you can not vote for whoever is the strongest based on how many questions were answered correctly, how long it took, and how many points were banked.

# Rounds
Each player is asked a random question from the questions.csv file. I need to add more questions to this. If it is a correct answer, the arrow points at a higher value, and the next player gets 1 second to bank. Banking saves all the points below the arrow into the bank, but resets the arrow to the bottom. If a question is wrong, the arrow is reset and a new chain is started. If you bank 1000 points, then the round will instantly end, if you bank over 1000 points, it will only count as 1000 points. A player must click bank as there is no automatic banking, if you get the arrow past 1000 and do not bank, it will just stay there until you bank 1000 so make sure you are paying attention to the total. If you run out of time, you will lose everything in the chain. The first lasts 180 seconds, and the time decreases by 10 seconds after each round. If there are less than 9 players, the first round will be 180 - (9 - total players) times 10 seconds, (to put it simply, it will start with less time the less players). However, the last round will be only 90 seconds (and the first round will be 90 seconds if there are just 2 players), but whatever you win will be trebled. At the end of a round (except the last one where it goes to a head to head), the weakest link will be voted.

# Voting
Each player decides the weakest link after a round. The player with the most votes will be eliminated. You cannot vote for yourself and you cannot vote for the strongest link if that setting is enabled. If there is a draw, the statistical strongest link will vote for the players in a draw. Whoever is voted for is eliminated. It will reveal who everyone voted for as well as the statistical strongest link and weakest link after everyone has voted. CPUs, regardless of difficulty, will almost always vote for the statistical weakest link.

# After the final round
No voting takes place after the final round. Instead, a head to head occurs (known as the final). Each player is asked 5 questions in turn, and whoever has the most correct wins. If a player will always lose (cannot win) even by answering the rest the questions correctly and its opponent answering the rest of the questions incorrectly, then its opponent will automatically win. Correct answers are shown with a + on the bottom, incorrect answers are shown with a - on the bottom. If there is a draw after 5 questions, then sudden death is played until there is a winner.

# Sudden Death
During sudden death, each player answers one question in turn. A correct answer is shown with a + and an incorrect answer is shown with a -. If one gets its question right and the other gets its question wrong, the player with the correct answer automatically wins. If both get it wrong, or both get it right, each player answers another question until there is a winner. 

# Victory
The player who wins gets all of the points and the player who loses gets nothing. The winning player is declared the strongest link. The game then ends and closes after the final music plays. 
