# Student: Branden Lee

# oska.py
# some examples:
# movegen(['-----','--wb','-b-','--','-w-','bbbb','-b---'],'b')
# movegen(['-----','--wb','-b-','--','-w-','bbbb','-b---'],'w')
# movegen(['wwww','-b-','--','---','bbbb'],'b')

from queue import PriorityQueue
import math


# movegen function
# generates moves given a state array and side
# returns a list of serialized states
# it is up to the adversarial state search function in assignment 4
# to remove states that have already been visited
# Board position naming
# -------------------
# | 00 | 01 | 02 | 03 |
# -------------------
#   | 04 | 05 | 06 |
#    --------------
#      | 07 | 08 |
#    --------------
#   | 09 | 10 | 11 |
# -------------------
# | 12 | 13 | 14 | 15 |
# -------------------
def movegen(state_array, side):
    new_state_list = []
    # first the array is serialized
    state_id = serialize(state_array)
    width = len(state_array[0])
    pos_row_table = get_pos_row_table(width)
    pos_tot = width_to_pos_tot(width)
    rows_tot = width_to_rows_tot(width)
    if side == 'b':
        opponent = 'w'
    else:
        opponent = 'b'
    for pos in range(0, pos_tot):
        if state_id[pos] == side:
            row_info = pos_row_table[pos]
            # blue goes up
            if side == 'b':
                new_state_id = try_top_left(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
                new_state_id = try_top_right(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
            # white goes up
            if side == 'w':
                new_state_id = try_bottom_left(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
                new_state_id = try_bottom_right(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
    printPath(new_state_list)
    # return new_state_list


# Returns unique state identifier
# state[] example:
#  -------------------
# |  W |  W |  W |    |
#  -------------------
#   |    |    |  W |
#    --------------
#      |    |    |
#    --------------
#   |    |    |    |
#  -------------------
# |  B |  B |  B |  B |
#  -------------------
# becomes =>
# State.id: WWW---W-----BBBB
def serialize(state_array):
    return ''.join(state_array)


# Returns a python dictionary
# that acts as table for position => row info
def get_pos_row_table(width):
    pos_row_table = {}
    pos_tot = width_to_pos_tot(width)
    for pos in range(0, pos_tot):
        row: int
        row, row_pos, row_width, row_depth = pos_to_row(pos, width)
        row_info = {}
        row_info["row"] = row
        row_info["row_pos"] = row_pos
        row_info["row_width"] = row_width
        row_info["row_depth"] = row_depth
        pos_row_table[pos] = row_info
    return pos_row_table


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_top_left(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == 0:
        return None
    if row_info["row_depth"] > 0 and row_info["row_pos"] == 0:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth <= 0:
        row_depth = abs(row_depth) + 1
    pos_try = pos - (row_depth + 2)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_top_left(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_top_right(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == 0:
        return None
    if row_info["row_depth"] > 0 and row_info["row_pos"] == row_info["row_width"] - 1:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth <= 0:
        row_depth = abs(row_depth) + 1
    pos_try = pos - (row_depth + 1)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_top_right(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_bottom_left(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == rows_tot - 1:
        return None
    if row_info["row_depth"] < 0 and row_info["row_pos"] == 0:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth >= 0:
        row_depth = abs(row_depth) + 1
    else:
        row_depth = abs(row_depth)
    pos_try = pos + (row_depth + 1)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_bottom_left(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_bottom_right(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == rows_tot - 1:
        return None
    if row_info["row_depth"] < 0 and row_info["row_pos"] == row_info["row_width"] - 1:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth >= 0:
        row_depth = abs(row_depth) + 1
    else:
        row_depth = abs(row_depth)
    pos_try = pos + (row_depth + 2)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_bottom_right(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# convert board total board positions to first row width
def pos_tot_to_width(pos_tot):
    return int((-1 + int(math.sqrt(17 + 4 * pos_tot))) / 2)


# convert first row width to board total board positions
def width_to_pos_tot(width):
    return int(width * width + width - 4)


# convert first row width to board total board positions
def width_to_rows_tot(width):
    return int(2 * width - 3)


# convert pos to row number and row position
# @param width Max width of board.
# @return row The row number starting from 0 and increasing downward.
# @return row_pos The position on the row starting from 0 and increasing right.
# @return row_width The width of the row
# @return row_depth The depth of the rwo from the shortest row
# negative goes upward and positive down, zero is center
def pos_to_row(pos, width):
    rows_tot = width_to_rows_tot(width)
    pos_tot = width_to_pos_tot(width)
    pos_mid = pos_tot / 2 - 1
    # this mathematical series calculation below has
    # has only been tested with width < 6
    if pos <= pos_mid + 1:
        row_depth_float = (((-1 + math.sqrt(8 * pos_mid - 8 * pos + 25)) / 2) - 2) * -1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        # but is sufficient for this assignment
        row_pos = math.ceil((row_depth_float - row_depth) * row_width)
    else:
        row_depth_float = ((-1 + math.sqrt(8 * pos - 8 * pos_mid + 9)) / 2) - 1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        row_pos = math.floor((row_depth_float - row_depth) * row_width)
    # width of the row
    row = int(row_depth + (rows_tot - 1) / 2)
    return row, row_pos, row_width, row_depth


# writes the stateId to a readable board on the console
# example:
#  -------------------
# |  W |  W |  W |    |
#  -------------------
#   |    |    |  W |
#    --------------
#      |    |    |
#    --------------
#   |    |    |    |
#  -------------------
# |  B |  B |  B |  B |
#  -------------------
# pos_row_table is a hash table mapping position -> row
def print_state(state_id):
    pos_tot = len(state_id)
    width = pos_tot_to_width(pos_tot)
    rows_tot = width_to_rows_tot(width)
    print(' ' * 2, end='')
    print('-' * 3 * width)
    for pos in range(0, pos_tot):
        row, row_pos, row_width, row_depth = pos_to_row(pos, width)
        indent = width - row_width
        if row_pos == 0:
            print(' ' * 2 * indent, end='')
            print("| ", end='')
        else:
            print(" | ", end='')
        if state_id[pos] != '-':
            print(state_id[pos], end='')
        else:
            print(' ', end='')
        if row_pos == row_width - 1:
            print(" |")
            print(' ' * 2 * (indent + 1), end='')
            print('-' * 3 * row_width)


# writes the stateId to readable board to file
def write_state(file_handle, state_id):
    for i in range(0, 36):
        file_handle.write(state_id[i])
        if i % 6 == 5:
            file_handle.write("\n")


# Writes the path of states to the console.
def printPath(path):
    n = len(path)
    for i in range(0, n):
        print_state(path[i])
        print("\n", end='')


# Writes the path of states to a file.
def write_path(file_handle, path):
    n = len(path)
    for i in range(0, n):
        file_handle.write("Move: " + str(i) + "\n")
        write_state(file_handle, path[i])
        file_handle.write("\n")


# FOR DEBUG USE
# writes the parent state board to a file
def debug_file_state(file_handle, state_pair, queue):
    file_handle.write("==============================================\n")
    file_handle.write("PriorityQueue.length = " + str(queue.qsize()) + "\n")
    file_handle.write("Priority " + str(state_pair[0]) + "\n")
    write_state(file_handle, state_pair[1].id)


# FOR DEBUG USE
# writes the child or successor state board to a file
def debug_file_child_state(file_handle, state_pair):
    file_handle.write("CHILD Priority " + str(state_pair[0]) + "\n")
    write_state(file_handle, state_pair[1].id)
