from next_track import next_track
import responses
import json

STATUS = {
    "is_playing": True,
    "item": {
        "name": "Gary",
        "artists": [{"name": "George"}],
    },
    "device": {"name": "device"},
}


class TestCLISpotify:
    @responses.activate
    def test_status(self):
        session = next_track.CLISpotify()

        responses.get(
            "https://api.spotify.com/v1/me/player",
            status=200,
            json=STATUS,
        )

        status = session.status()
        assert status == "Now Playing: Gary by George on device"

    @responses.activate
    def test_search_play(self):
        session = next_track.CLISpotify()

        responses.get("https://api.spotify.com/v1/me/player")
        responses.put("https://api.spotify.com/v1/me/player/play", status=200)
        responses.get(
            "https://api.spotify.com/v1/search?q=radiohead&type=artist",
            status=204,
            json={"artists": {"items": [{"id": 12345}]}},
        )

        play_json = json.loads(
            session.search_play(search_type="artist", name="radiohead")
        )

        assert play_json["item_id"] == 12345
        assert play_json["status"] == 200

    @responses.activate
    def test_next_track(self):
        session = next_track.CLISpotify()

        responses.get(
            "https://api.spotify.com/v1/me/player",
            status=200,
            json=STATUS,
        )
        responses.post("https://api.spotify.com/v1/me/player/next", status=204)

        assert session.next_track() == "playing"

    @responses.activate
    def test_pause_track(self):
        session = next_track.CLISpotify()

        responses.put("https://api.spotify.com/v1/me/player/pause", status=204)
        responses.get(
            "https://api.spotify.com/v1/me/player",
            status=200,
            json=STATUS,
        )

        assert session.pause_track() == "paused"
