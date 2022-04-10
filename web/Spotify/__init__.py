from web.Spotify.get_token import get_token
from web.Spotify.get_genres import get_genres
from web.Spotify.get_reco_tracks import get_reco_tracks
from web.Spotify.get_features import get_features
from web.Spotify.Spotify import Spotify

__version__ = "1.0.0"
__all__ = ["get_token", "get_reco_tracks"
           "get_genres", "get_features", "Spotify"]
