#!/usr/bin/env python3
import curses


def main(stdscr):
    try:
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        
        # pad1 = curses.newpad(5, 50)
        # pad1.addstr(0, 0, "up left\nhi there")
        # pad1.addstr(4, 0, "bottom left")
        # pad1.addstr(0, 41, "up right")
        # pad1.addstr(4, 37, "bottom right")
        # pad1.refresh(0, 0, 0, 0, 4, 50)
        
        pad2 = curses.newpad(7, 30)
        pad2.addstr(0, 0, "up left\nhi there")
        pad2.addstr(5, 0, "bottom left")
        pad2.addstr(0, 22, "up right")
        pad2.addstr(5, 18, "bottom right")
        pad2.refresh(0, 0, 5, 0, 11, 30)
        curses.napms(5000)
        # stdscr.refresh()

    except KeyboardInterrupt:
        curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
