#!/usr/bin/env python3
import curses


def main(stdscr):
    try:
        curses.start_color()
        curses.use_default_colors()

        try:
            curses.init_pair(228, 227, -1)  # Yellow
            curses.init_pair(48, 47, -1)  # Green
            curses.init_pair(198, 197, -1)  # Red

            stdscr.addstr(0, 0, 'amarillo', curses.color_pair(228))
            stdscr.addstr(1, 0, 'verde', curses.color_pair(48))
            stdscr.addstr(2, 0, 'rojo', curses.color_pair(198))
            stdscr.refresh()
            curses.napms(20000)
        except curses.ERR:
            pass

    except KeyboardInterrupt:
        curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
