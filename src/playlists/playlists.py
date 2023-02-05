import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from pick import pick
from spotipy.oauth2 import SpotifyOAuth

from database.db import Database
from next_track.next_track import CLISpotify

load_dotenv()

BASE_URL = "https://api.spotify.com/v1/"
SCOPE = "user-read-playback-state,user-modify-playback-state,playlist-read-private,playlist-modify-private"
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

SESSION = CLISpotify()


class Playlist:
    def client(
        self, method, endpoint, json=None, params=None
    ) -> requests.models.Response:
        r = requests.request(
            method=method,
            url=BASE_URL + endpoint,
            headers=HEADERS,
            json=json,
            params=params,
        )
        return r

    def get_my_playlists(self):
        pl_list = []
        playlists = self.client(method="GET", endpoint="me/playlists")
        for item in playlists.json()["items"]:
            pl_list.append((item["name"], item["id"]))

        return pl_list

    def play_playlist(self, playlist_id: str):
        context_uri = f"spotify:playlist:{playlist_id}"
        json = {"context_uri": context_uri}

        r = self.client(method="PUT", endpoint="me/player/play", json=json)
        print(r.text)

        # I just like to shuffle my playlists
        self.shuffle(True)

        return {"status": r.status_code, "playlist_id": playlist_id}

    def shuffle(self, state: bool):
        params = {"state": state}
        r = self.client(method="PUT", endpoint="me/player/shuffle", params=params)
        return {"status": r.status_code, "state": state}

    def add_current_to_playlist(self, playlist_id):
        uri = self.get_current_track()
        r = self.client(
            method="POST",
            endpoint=f"playlists/{playlist_id}/tracks",
            json={"uris": [uri]},
        )
        return {"status": r.status_code, "snapshot_id": r.json()["snapshot_id"]}

    def get_current_track(self):
        r = self.client(method="GET", endpoint="me/player")
        return r.json()["item"]["uri"]


if __name__ == "__main__":
    pl = Playlist()

    if sys.argv[1] == "play":
        option_list = []
        for i in pl.get_my_playlists():
            option_list.append(i[0])

        option, index = pick(option_list, "Select a Playlist: ")

        pl.play_playlist(playlist_id=pl.get_my_playlists()[index][1])

        time.sleep(1)

        SESSION.status()

    if sys.argv[1] == "add":
        pl.add_current_to_playlist("7JcJWgaDeQS1CUXDsBlJ5X")  # Terminal Tracks
        with Database("my_db.db") as db:
            db.write(table="spotify", data=SESSION.status())
            q = db.getLast(table="spotify", columns="track, artist")
            print(f"{q[0]} by {q[1]} added to database")
    if sys.argv[1] == "current":
        print(pl.get_current_track())