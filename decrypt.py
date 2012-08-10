#!/usr/bin/env python
import curses
import time
import fileinput
import random
import string
import re
import sys

lines = []
chance = 0.1
confirmed_per_line = []

screen = curses.initscr()
curses.start_color()
curses.noecho()
try:
    curses.curs_set(0)
except:
    pass
screen.keypad(1)

attr = 0
foreground = curses.COLOR_WHITE
background = curses.COLOR_BLACK
color_pairs = [0] * 64
colnum = 1

def reset_attrs():
    global attr
    global foreground
    global background
    attr = 0
    foreground = curses.COLOR_WHITE
    background = curses.COLOR_BLACK

def get_color_pair(col1, col2):
    global colnum
    global color_pairs
    p = color_pairs[col1 + col2 * 8]
    if p:
        return p
    curses.init_pair(colnum, col1, col2)
    color_pairs[col1 + col2 * 8] = colnum
    colnum += 1
    return color_pairs[col1 + col2 * 8]

def write_coloured_line(row, line):
    global attr
    global foreground
    global background
    global colnum

    screen.move(row, 0)

    current = []
    col = 0
    color = get_color_pair(foreground, background)
    for char in line:
        if len(char) == 1:
            current.append(char)
        else:
            if len(current) > 0:
                try:
                    screen.addstr(row, col, ''.join(current), attr | curses.color_pair(color))
                except:
                    pass
                col += len([c for c in current if len(c) == 1])
                current = []
            attrs = [int(code) if len(code) > 0 else 0 for code in char[2:-1].split(";")]
            colours = [curses.COLOR_BLACK,
                       curses.COLOR_RED,
                       curses.COLOR_GREEN,
                       curses.COLOR_YELLOW,
                       curses.COLOR_BLUE,
                       curses.COLOR_MAGENTA,
                       curses.COLOR_CYAN,
                       curses.COLOR_WHITE]
            for code in attrs:
                if code == 0:
                    reset_attrs()
                elif code == 1:
                    attr |= curses.A_BOLD
                elif code == 4:
                    attr |= curses.A_UNDERLINE
                elif code == 5:
                    attr |= curses.A_BLINK
                elif code == 7:
                    attr |= curses.A_REVERSE
                elif code >= 30 and code < 38:
                    foreground = colours[code - 30]
                elif code >= 40 and code < 48:
                    background = colours[code - 40]

            color = get_color_pair(foreground, background)

    if len(current) > 0:
        try:
            screen.addstr(row, col, ''.join(current), attr)
        except:
            pass
        current = []

    screen.clrtoeol()

def iterate(increase = False):
    still_random = 0
    global chance, confirmed_per_line, lines
    if increase:
        chance += 0.01
#    screen.erase()
    (y,x) = screen.getmaxyx()
    start_line = y - min(len(lines), y)
    final_line = len(lines)
    if final_line > y:
        first_line = final_line - y
    else:
        first_line = 0
    reset_attrs()
    for line_num in range(first_line, final_line):
        line = lines[line_num]
        for i in [i  for i in range(min(x, len(line))) if i not in confirmed_per_line[line_num]]:
            still_random += 1
            if random.random() < chance:
                confirmed_per_line[line_num].append(i)
        random_line = [random.choice(string.punctuation)
                       if col not in confirmed_per_line[line_num]
                       else line[col]
                       for col in range(min(len(line), x))]
        write_coloured_line(start_line + line_num - first_line, random_line)

    screen.refresh()
    time.sleep(0.1)
    return still_random > 0

char_re = re.compile("\x1b\\[\\d*(?:;\\d+)*m|[\x20-\xff]")

try:
    for line in fileinput.input():
        confirmed_per_line.append([])
        lines.append(list(m.group(0) for m in char_re.finditer(line.rstrip())))
        iterate()
    confirmed_per_line.append([])
    lines.append([])
    fileinput.close()
    while iterate(True):
        pass
finally:
    curses.endwin()
