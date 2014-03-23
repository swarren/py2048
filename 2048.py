#!/usr/bin/python3

# Copyright (c) 2014, Stephen Warren
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.import random

import random
import sys
import termios
import tty

DIR_LEFT = 0
DIR_RIGHT = 1
DIR_UP = 2
DIR_DOWN = 3

xs = ys = 4

def board_index(x, y):
    return (y * ys) + x

def print_board(board):
    for y in range(ys):
        print('+----' * xs + '+')
        for x in range(xs):
            val = board[board_index(x, y)]
            if val:
                cell = '% 4d' % val
            else:
                cell = '    '
            print('|' + cell , end='')
        print('|')
    print('+----' * xs + '+')

def add_piece(board):
    empty_positions = [i for i, val in enumerate(board) if val == 0]
    insert_pos = random.randint(0, len(empty_positions) - 1)
    board[empty_positions[insert_pos]] = 1
    return board

def getch():
    fd = sys.stdin.fileno()
    orig_termios_attr = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, orig_termios_attr)
    return ch

rows_l2r_t2b = [[board_index(x, y) for x in range(xs)] for y in range(ys)]
rows_r2l_t2b = [[board_index(xs - x - 1, y) for x in range(xs)] for y in range(ys)]

cols_t2b_l2r = [[board_index(x, y) for y in range(ys)] for x in range(xs)]
cols_b2t_l2r = [[board_index(x, ys - y - 1) for y in range(ys)] for x in range(xs)]

pos_lists_of_move = {
    DIR_LEFT:  rows_l2r_t2b,
    DIR_RIGHT: rows_r2l_t2b,
    DIR_UP:    cols_t2b_l2r,
    DIR_DOWN:  cols_b2t_l2r,
}

def apply_move(board, move):
    pos_lists = pos_lists_of_move[move]
    for pos_list in pos_lists:
        dst = 0
        for src in range(len(pos_list)):
            if board[pos_list[src]]:
                board[pos_list[dst]] = board[pos_list[src]]
                dst += 1
        for i in range(dst, len(pos_list)):
            board[pos_list[i]] = 0
        for i in range(len(pos_list[:-1])):
            if board[pos_list[i]] == board[pos_list[i + 1]]:
                board[pos_list[i]] += board[pos_list[i + 1]]
                for j in range(i + 1, len(pos_list) - 1):
                    board[pos_list[j]] = board[pos_list[j + 1]]
                board[pos_list[-1]] = 0
    return board

move_dir_map = {
    'h': DIR_LEFT,
    'j': DIR_DOWN,
    'k': DIR_UP,
    'l': DIR_RIGHT,
}

def get_apply_move(board):
    while True:
        print('Move: ', end='')
        sys.stdout.flush()
        ch = getch().lower()
        print(ch)
        if ch == 'q':
            print('Quitting')
            sys.exit(0)
        if ch == 'p':
            print_board(board)
            continue
        if ch not in move_dir_map:
            print('Unknown move (h/j/k/l/p/q)')
            continue
        move = move_dir_map[ch]
        new_board = apply_move(board.copy(), move)
        if new_board == board:
            print('Illegal move')
            continue
        break
    print()
    return add_piece(new_board)

board = [0] * (ys * xs)
board = add_piece(board)

detect_2048 = True
while True:
    print_board(board)
    if detect_2048 and 2048 in board:
        while True:
            print('You win; Continue/Quit? ', end='')
            sys.stdout.flush()
            ch = getch().lower()
            print(ch)
            if ch == 'q':
                print('Quitting')
                sys.exit(0)
            if ch == 'c':
                print('Continuing')
                detect_2048 = False
                break
            print('Unknown option (c/q)')
    moves_left = False
    for move in (DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN):
        new_board = apply_move(board.copy(), move)
        if new_board != board:
            moves_left = True
            break
    if not moves_left:
        print('You lose!')
        sys.exit(0)
    board = get_apply_move(board)
