DOMAIN = "pykomfovent"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300
FILTER_WARNING_THRESHOLD = 80

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

# Mode mappings (key -> possible values from device in different languages)
MODES = {
    "away": ("AWAY", "NIEOBECNOŚĆ", "NIEOBECNOSC"),
    "normal": ("NORMAL", "NORMALNY"),
    "intensive": ("INTENSIVE", "INTENSYWNY"),
    "boost": ("BOOST", "TURBO"),
}
