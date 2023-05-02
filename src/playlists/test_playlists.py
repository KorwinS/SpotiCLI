import playlists
import responses
import pytest
import time

PL_LIST = [("My Playlist", "123456")]
BASE_URL = "https://api.spotify.com/v1/"


class TestPlaylists:
    @pytest.fixture
    def session(self):
        session = playlists.Playlist()
        return session

    @responses.activate
    def test_get_my_playlists(self, session):
        responses.get(
            BASE_URL + "me/playlists",
            json={"items": [{"name": "My Playlist", "id": "123456"}]},
        )
        pl_list = session.get_my_playlists()

        assert pl_list == PL_LIST

    @responses.activate
    def test_play_playlist(self, session):
        responses.put(BASE_URL + "me/player/shuffle", status=204)
        responses.put(BASE_URL + "me/player/play", status=204)
        assert session.play_playlist(playlist_id="1234arst") == {
            "status": 204,
            "context_uri": "spotify:playlist:1234arst",
        }

    @responses.activate
    def test_shuffle(self, session):
        responses.put(BASE_URL + "me/player/shuffle", status=204)
        assert session.shuffle(state=True) == {"status": 204, "state": True}
        assert session.shuffle(state=False) == {"status": 204, "state": False}

    @responses.activate
    def test_add_current_to_playlist(self, session):
        playlist_id = "23i4en27547iek"
        responses.post(
            BASE_URL + f"playlists/{playlist_id}/tracks",
            json={"snapshot_id": "arst1234"},
            status=200,
        )
        responses.get(
            BASE_URL + "me/player",
            status=200,
            json={"item": {"uri": "spotify:track:324enh2894ht"}},
        )

        assert session.add_current_to_playlist(playlist_id=playlist_id) == {
            "status": 200,
            "snapshot_id": "arst1234",
        }

    @responses.activate
    def test_get_current_track(self, session):
        responses.get(
            BASE_URL + "me/player",
            status=200,
            json={"item": {"uri": "spotify:track:324enh2894ht"}},
        )
        assert session.get_current_track().startswith("spotify:track")

    @responses.activate
    def test_find_duplicates(self, session):
        responses.get(
            BASE_URL + "playlists/w09n23ient9ie/tracks",
            json={
                "items": [
                    {"track": {"id": "abc12345"}},
                    {"track": {"id": "xyz09876"}},
                    {"track": {"id": "abc12345"}},
                ]
            },
        )
        assert session.find_duplicates("w09n23ient9ie") == ["abc12345"]

    @responses.activate
    def test_delete_tracks(self, session):
        responses.delete(
            BASE_URL + "playlists/ot293ne42tnu/tracks", json={"snapshot_id": "abc123"}
        )
        track_list = ["abc123", "xyz098"]
        assert session.delete_tracks(
            track_list=track_list, playlist_id="ot293ne42tnu"
        ) == {"snapshot_id": "abc123"}

    @responses.activate
    def test_recommend(self, session):
        responses.get(BASE_URL + "recommendations", json={"abc": "123"})
        assert session.recommend(seed_tracks=["abc", "def"]) == {"abc": "123"}
