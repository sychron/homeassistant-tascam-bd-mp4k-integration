from homeassistant.components.media_player import MediaPlayerEntityFeature

DOMAIN = "tascam_bdmp4k"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"
DEFAULT_PORT = 9030
DEFAULT_NAME = "BD-MP4K"

SUPPORT_TASCAM = (
    MediaPlayerEntityFeature.TURN_ON |
    MediaPlayerEntityFeature.TURN_OFF |
    MediaPlayerEntityFeature.PLAY |
    MediaPlayerEntityFeature.PAUSE |
    MediaPlayerEntityFeature.STOP
)
