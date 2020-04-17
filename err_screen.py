import draw_tools as draw
import traceback


_BGCOLOR = 40
_TEXTCOLOR = 31
_TITLEBGCOLOR = 47
_TITLETEXTCOLOR = 30

_ERR_TITLE = 'OOPS!'

_ERR_TEXT = \
'''
/Unfortunately, 
/
/NPMGR has made a serious mistake and NPMGR will be forced to quit.
/
'''

def handle_exception(exc_type, exc_value, exc_tb, kidding=False):
    # Fill screen    
    for y in range(draw.ln() - 1):
        draw.puts(0, y+2, draw.bgstr(' '*draw.col(), _BGCOLOR, _TEXTCOLOR))
    
    draw.puts(0, 0, '')

    if kidding:
        f = ['I JUST KIDDING...\n']
    else: 
        f = traceback.format_exception(exc_type, exc_value, exc_tb)
    
    for fl in _ERR_TEXT.split('/') + f:
        print(draw.bgstr(fl, _BGCOLOR, _TEXTCOLOR), end='')

    draw.tprint(0, 0, draw.bgstr(' '*draw.col(), _TITLEBGCOLOR, _TITLETEXTCOLOR))
    draw.tprint(int(draw.col() / 2 - len(_ERR_TITLE) / 2), 0, 
                draw.bgstr(_ERR_TITLE, _TITLEBGCOLOR, _TITLETEXTCOLOR))
    
    input(draw.bgstr('\n [Enter to exit]', _BGCOLOR, _TEXTCOLOR))
    draw.clear()
