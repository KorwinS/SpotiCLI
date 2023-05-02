import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

BASE_URL = "https://api.spotify.com/v1"
SCOPE = "user-read-playback-state,user-modify-playback-state"
CREDS = SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri=os.getenv("CALLBACK_URI"),
    scope=SCOPE,
)

TOKEN = CREDS.get_access_token(as_dict=False)
HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Content-Type": "application/json",
}


class CLISpotify:
    def client(self, method, endpoint, params=None, json=None):
        r = requests.request(
            method=method,
            url=BASE_URL + endpoint,
            params=params,
            json=json,
            headers=HEADERS,
        )
        return r

    def next_track(self):
        r = self.client(method="POST", endpoint="/me/player/next")
        print(r.text)
        if r.status_code == 204:
            return "playing"
        else:
            return "no session to play"

    def pause_track(self):
        r = self.client(method="PUT", endpoint="/me/player/pause")
        print(r.text)
        if r.status_code == 204:
            return "paused"
        return "no session to pause"

    def item_lookup(self, search_type: str, q: str):
        search = self.client(
            method="GET", endpoint="search", params={"q": q, "type": search_type}
        )
        if search_type == "album":
            # I don't want shuffle on for albums, so this turns it off
            self.client(
                method="PUT", endpoint="/me/player/shuffle", params={"state": False}
            )
        # take the first one for now, iterate later
        return search.json()[f"{search_type}s"]["items"][0]["id"]

    def search_play(self, search_type: str, name: str):
        # Look up item
        item_id = self.item_lookup(search_type=search_type, q=name)
        paylaod = {
            "context_uri": f"spotify:{search_type}:{item_id}",
            "position_ms": 0,
        }
        # print(paylaod)
        player = self.client(method="PUT", endpoint="/me/player/play", json=paylaod)
        print(player.text)
        return json.dumps({"item_id": item_id, "status": player.status_code})

    def status(self):
        r = self.client(method="GET", endpoint="/me/player")
        if r.status_code == 200 and r.json()["is_playing"] is True:
            item = r.json()["item"]
            message = f"Now Playing: {item['name']} by {item['artists'][0]['name']} on {r.json()['device']['name']}" # noqa
            print(message)
            return [item["artists"][0]["name"], item["name"], item["uri"]]

        else:
            message = "Not playing anywhere"
            print(message)
            return message

    def help(self):
        print(
            """
Options:
'next' to advance the next track
'pause' pauses the music
'status' shows current player status
'player <search type> <query>' accepts 'artist' or 'album' for search type, the artist
or album name for the query
"""
        )


if __name__ == "__main__":
    session = CLISpotify()
    if sys.argv[1] == "help" or sys.argv is None:
        session.help()
    elif sys.argv[1] == "next":
        session.next_track()
        session.status()
    elif sys.argv[1] == "pause":
        print("pausing...")
        session.pause_track()
    elif sys.argv[1] == "play":
        session.search_play(search_type=sys.argv[2], name=sys.argv[3])
        time.sleep(1)  # avoids a race condition with the status call below
        session.status()
    elif sys.argv[1] == "status":
        session.status()
