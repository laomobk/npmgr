import err_screen
# import draw_tools as draw

def _EGG_NEZHAISCUTE():
    while True:
        print('You are right.')


def _EGG_IJUSTWANTANEXCEPTION():
    raise Exception('You just want an exception')


def check_egg(cmd :str) -> str:
    if len(cmd) > 1 and (cmd[0], cmd[-1]) == ('<', '>'):
        c = cmd[1:-1]

        f = globals().get('_EGG_' + c, None)

        if f is None:
            return cmd

        f()

        return ''
    return cmd
