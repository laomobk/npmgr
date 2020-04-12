# Key code for npmgr

KEY_UP = b'\033[A'
KEY_DOWN = b'\033[B'
KEY_ENTER = b'\n'
KEY_RETURN = b'\r'
KEY_EOF = b'\x04'
KEY_ALT_SPACE = b'\x1b '
KEY_ESC = b'\033'

KEY_COLON = b':'

KEY_S = b's'

UNKNOWN_KEY = -1

K_MAP = {
         b'\x1b[A' : KEY_UP,
         b'\x1b[B' : KEY_DOWN,
        }
