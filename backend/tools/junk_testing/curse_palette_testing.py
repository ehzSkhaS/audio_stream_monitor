#!/usr/bin/env python3
import curses


def main(stdscr):
    try:
        curses.start_color()
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        try:
            for i in range(0, 255):
                stdscr.addstr(str(i) + ' ', curses.color_pair(i))
            stdscr.refresh()
            curses.napms(20000)
        except curses.ERR:
            pass

    except KeyboardInterrupt:
        curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
