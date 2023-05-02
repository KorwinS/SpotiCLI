import sys
import time

from pick import pick

from database.db import Database
from next_track.next_track import CLISpotify
from playlists.playlists import Playlist

SESSION = CLISpotify()
TT_PLAYLIST = "7JcJWgaDeQS1CUXDsBlJ5X"
DB_PATH = "/Users/korwin/code/spotify/my_db.db"
PL = Playlist()


def play() -> str:
    """Finds a user's playlist to play

    Returns:
        str: the selected playlist name
    """
    option_list = []
    for i in PL.get_my_playlists():
        option_list.append(i[0])

    option, index = pick(option_list, "Select a Playlist: ")
    PL.play_playlist(playlist_id=PL.get_my_playlists()[index][1])
    time.sleep(1)
    SESSION.status()
    return option


def dedupe() -> tuple:
    """finds and deletes duplicate tracks in a playlist

    Returns:
        tuple: the list of tracks, the playlist selected
    """
    option_list = []

    p_lists = PL.get_my_playlists()

    for i in p_lists:
        # print(i[1])
        option_list.append(i[0])

    option, index = pick(option_list, "Select Playlist to Deduplicate:")
    dupes = PL.find_duplicates(p_lists[index][1])
    PL.delete_tracks(track_list=dupes, playlist_id=p_lists[index][1])
    return (dupes, option)


def add() -> tuple:
    """Adds the current track to a playlist

    Returns:
        tuple: the track, the artist
    """
    PL.add_current_to_playlist(TT_PLAYLIST)  # Terminal Tracks
    with Database(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS spotify (artist, track, track_uri)")
        db.write(table="spotify", data=SESSION.status())
        q = db.getLast(table="spotify", columns="track, artist")
        print(f"{q[0]} by {q[1]} added to database")
    return (q[0], q[1])


def recommend() -> str:
    """Gets a reccomended track based on the currently playing track

    Returns:
        str: the selected recommendation
    """
    current = PL.get_current_track()
    # print(current)

    results = list()
    rec = PL.recommend(current.split(":")[2])
    # for i in rec.json()["tracks"]:
    for i in rec["tracks"]:
        results.append((i["name"], i["uri"]))

    options = []
    for i in results:
        options.append(i[0])
    option, index = pick(options, "For you to browse")
    PL.client(
        method="PUT", endpoint="me/player/play", json={"uris": [results[index][1]]}
    )
    time.sleep(1.5)
    SESSION.status()
    return option


if __name__ == "__main__":
    # pl = Playlist()

    if sys.argv[1] == "play":
        play()

    if sys.argv[1] == "dedupe":
        dedupe()

    if sys.argv[1] == "add":
        add()

    if sys.argv[1] == "current":
        print(PL.get_current_track())

    if sys.argv[1] == "recommend":
        recommend()

    if sys.argv[1] == "next":
        CLISpotify().next_track()
