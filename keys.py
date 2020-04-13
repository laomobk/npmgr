# Key code for npmgr

KEY_UP = b'\033[A'
KEY_DOWN = b'\033[B'
KEY_ENTER = b'\n'
KEY_RETURN = b'\r'
KEY_EOF = b'\x04'
KEY_ALT_SPACE = b'\x1b '
KEY_ESC = b'\033'
KEY_PGUP = b'\x1b[5~'
KEY_PGDOWN = b'\x1b[6~'

KEY_COLON = b':'

KEY_m = b'm'
KEY_s = b's'
KEY_q = b'q'
KEY_j = b'j'

UNKNOWN_KEY = -1

K_MAP = {
         b'\x1bOA' : KEY_UP,
         b'\x1bOB' : KEY_DOWN,
        }
