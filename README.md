# LoL Analytics and Win Probability Calculator - WIP
This is a League of Legends analytics tool (and soon to be a win probability estimator) that calculates various statistics about a certain player, and this solves an issue I've noticed with all the major commercial tools - which is that they only show a few games' worth of stats. On top of that, there are a lot of stats that I have always been interested in, but I just could never obtain, so I decided to build a tool myself that can allow me to accurately identify certain areas where I have weaknesses and strengths when I play the game. This primarily uses Riot's REST APIs, Python, and SQLite

## Architecture Overview
```text
├── DB.py            # SQLite persistent layer & match caching
├── Riot_API.py      # Riot Games REST API handler & rate-limit logger
├── Player.py        # Calculation of various player statistics
├── Print_Stats.py   # CLI presentation & formatted terminal outputs
└── main.py          # Application entry point
```
1. The main.py file initialises the player.
2. When retrieving a match history, Player.py queries DB.py to check whether the JSON is already locally stored in the SQLite database; if it's missing, it requests match data via Riot_API.py whilst enforcing an API call budget of MAX_NEW_API_CALLS (of 50) to prevent rate limiting.
3. Player.py performs calculations to obtain various player statistics
4. All terminal formatting and output structures are decoupled from the rest of the program and handled exclusively by Print_Stats.py

## Features
### 1. Calculating overall win rate over X games
<img width="494" height="139" alt="WinRate" src="https://github.com/user-attachments/assets/e9e4ca9e-2fc6-4501-8c15-0f7f36d27451" />

Goes over all previous matches and tallies the wins and losses; skips corrupted matches (missing PUUIDs)  

### 2. Retrieving a specific player's champion masteries
<img width="179" height="522" alt="PlayersChampionMastery" src="https://github.com/user-attachments/assets/832c0f58-1c17-43e2-8706-bfd4d0665435" />  

Retrieves all the mastery data for that player and matches champion IDs to names  

### 3. Calculating win rate per champion over X games
<img width="513" height="1033" alt="ChampionKDAs" src="https://github.com/user-attachments/assets/757b9c2e-8b4e-4a87-b7cb-fdeefb42f360" />  

Goes over each match and determines the champion played and whether the player lost or won on them. Stored in a dictionary  

### 4. Calculating average KDA per champion over X games
<img width="535" height="1038" alt="AvgKDAPerChampion" src="https://github.com/user-attachments/assets/7630a0a9-6562-442c-8188-c43c1f053ff0" />  

Goes over each match and adds the kills, deaths, assists, and total matches for each champion in a dictionary, and calculates the average KDA over the total matches for that champion

### 5. Calculating win rate of current player with other players
<img width="459" height="388" alt="WinrateWithAllies" src="https://github.com/user-attachments/assets/b7ad41e8-86d1-444b-ad21-1abc7a7d7b1e" />  

Goes over each match and stores the PUUIDs of previous players played with in a dictionary and stores the total matches played with them. Optionally filters for only more than 1 match.

### 6. Calculating win rate of enemy players against current player
<img width="450" height="309" alt="WinrateOfEnemiesAgainstPlayer" src="https://github.com/user-attachments/assets/a40d2401-2b6d-426a-8892-c7099a676932" />  

Same principle as 6

### 7. Calculating win rate with ally champions
<img width="515" height="1171" alt="WinrateWithCertainAllyChampions" src="https://github.com/user-attachments/assets/8fd29492-8da8-4cb1-9e30-0cf8b727e6dd" />  

Goes over each match and stores the ally players' champion IDs in a dictionary, along with the total number of wins, losses, and matches played

### 8. Calculating win rate against enemy champions
<img width="529" height="1212" alt="WinrateAgainstCertainEnemyChampions" src="https://github.com/user-attachments/assets/8fae6984-b342-4cce-8b4b-47a70f93bddf" />  

Same principle as 7




