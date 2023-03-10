#!/usr/bin/env python3
import curses


def main(stdscr):
    inp = 0
    y, x = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.nodelay(1)
    while inp != 48 and inp != 27:
        while True:
            try:
                stdscr.addnstr(y-1, 0, 'I AM KILL TERMINAL WHEN RESIZE AAAAAAAH', x)
            except curses.error:
                pass
            inp = stdscr.getch()
            if inp != curses.KEY_RESIZE:
                break
            stdscr.erase()
            y, x = stdscr.getmaxyx()


if __name__ == "__main__":
    curses.wrapper(main)
