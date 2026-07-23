import sqlite3
import json

DB_PATH = 'lol_data.db'

# Setup connection to database path
def get_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.execute('PRAGMA foreign_keys=ON;')
  return conn

# Initalise the database with 3 tables
# Player: puuid, name, tag and region
# Match: match_id, time of creation, json payload
# Player_matches which acts a composite primary key as the player and matches are a many to many relationship

def init_db():
  with get_connection() as conn:
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
            puuid TEXT PRIMARY KEY,
            summoner_name TEXT,
            summoner_tag TEXT,
            region TEXT
        )""")

    c.execute("""CREATE TABLE IF NOT EXISTS matches (
            match_id TEXT PRIMARY KEY,
            game_creation INTEGER,
            json_data TEXT NOT NULL
        )""")

    c.execute("""CREATE TABLE IF NOT EXISTS player_matches (
            puuid TEXT,
            match_id TEXT,
            PRIMARY KEY(puuid, match_id),
            FOREIGN KEY(match_id) REFERENCES matches(match_id),
            FOREIGN KEY(puuid) REFERENCES players(puuid)
        )""")
    conn.commit()
  #print('Database schema ready')



def is_match_cached(match_id: str) -> bool:
  with get_connection() as conn:
    c = conn.cursor()
    c.execute(
        # Selects the first column from matches and checks for the 1st existence of whether the match exists in the database
        'SELECT EXISTS(SELECT 1 FROM matches WHERE match_id = ?)', (match_id,)
    )

    # returns a bool from the 1 or 0
    return bool(c.fetchone()[0])

def save_match_data(puuid: str, match_payload: dict, summoner_name: str, summoner_tag: str, region: str):
  match_id = match_payload['metadata']['matchId']
  game_creation = match_payload['info']['gameCreation']
  json_str = json.dumps(match_payload)

  with get_connection() as conn:
    c = conn.cursor()

    c.execute('INSERT OR IGNORE INTO players (puuid, summoner_name, summoner_tag, region) VALUES (?, ? ,?, ?)', (puuid, summoner_name, summoner_tag, region))

    c.execute(
        """
            INSERT OR IGNORE INTO matches (match_id, game_creation, json_data)
            VALUES (?, ?, ?)
        """,
        (match_id, game_creation, json_str),
    )

    # Link this player to this match
    c.execute(
        """
            INSERT OR IGNORE INTO player_matches (puuid, match_id)
            VALUES (?, ?)
        """,
        (puuid, match_id),
    )
    conn.commit()

def get_match_json(match_id: str) -> dict:
  with get_connection() as conn:
    c = conn.cursor()

    c.execute('SELECT json_data FROM matches WHERE match_id = ?', (match_id,))
    row = c.fetchone()

    # Converts the raw text string into a dictionary
    if row:
      return json.loads(row[0])
    return None

if __name__ == '__main__':
    init_db()