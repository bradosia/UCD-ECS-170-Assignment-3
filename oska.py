# Student: Branden Lee

# oska.py
# > oskaplayer(['wwww','---','--','---','bbbb'],'w',2)

from queue import PriorityQueue
import math


# n = # of first row elements
# startStateArray = 2n - 3 strings representing starting state
# side = white or black, which side to play
# depth = max moves to look ahead
def oskaplayer(start_state_array, side, depth):
    # n_row_0 = # of first row elements
    # pos_row_table hash table mapping position -> row
    start_state = serialize(start_state_array)
    pos_row_table = get_board_context(start_state)
    if pos_row_table is None:
        print("Start state is invalid!")
    else:
        path, states_explored = state_search(start_state, pos_row_table, side, depth)
        if path is None:
            print("No solution found.")
        else:
            printPath(path)
            print("Total moves:", len(path) - 1)  # subtract 1 because don't count start state
            print("Total states explored:", states_explored)
            # movesFileHandle = open("moves.txt", "w")
            # writePath(movesFileHandle, path)


# State
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
class State:
    __slots__ = ("id", "g", "h")

    def __init__(self):
        self.id = ""
        # g = node depth, h = heuristic value
        # f = g + h, but its the priority so it is stored in the priority queue
        self.g = self.h = 0

    # Tie breaker for equal priorities or f(n)
    # python requires me to add this. I arbitrarily compare h(n) as tie-breaker
    def __lt__(self, other):
        return self.h < other.h


# Iterative methods are faster than recursion
# This is basically a Best First Search of valid states
# implemented with a priority queue as the frontier.
def state_search(heuristic_mode, start_state_id, pieceTable):
    path = []
    # By default the priority queue orders by smallest first
    # this is the frontier
    queue = PriorityQueue()
    explored_table = {}
    goal_state_id = ""
    states_explored = 0
    start_state = State()
    start_state.id = start_state_id
    # debugFileHandle = open("debug.txt", "w")
    # the 2D arrays are serialized into a string
    # this makes hashing easier and allows string function use
    if mark_state_visited(start_state.id, "", explored_table):
        queue.put((0, start_state))
    while not queue.empty():
        states_explored = states_explored + 1
        currentStatePair = queue.get()
        currentState = currentStatePair[1]
        # debugFileState(debugFileHandle, currentStatePair, queue)
        # check if serialized current and goal state match
        if checkWinBoard(currentState.id):
            goal_state_id = currentState.id
            break
        else:
            newStateList = generatePossibleStates(currentState.id, pieceTable)
            n = len(newStateList)
            for i in range(0, n):
                if heuristic_mode == 0:
                    heuristicValue = calculate_heuristic_blocking(newStateList[i])
                elif heuristic_mode == 1:
                    heuristicValue = calculate_heuristic_custom(newStateList[i], pieceTable)
                else:
                    print("Error: Unknown heuristic mode ", heuristic_mode);
                    break
                if mark_state_visited(newStateList[i], currentState.id, explored_table):
                    # place new states in priority queue
                    newState = State()
                    newState.id = newStateList[i]
                    newState.h = heuristicValue
                    newState.g = currentState.g + 1
                    f = newState.g + newState.h
                    queue.put((f, newState))
                    # debugFileChildState(debugFileHandle,[heuristicValue, newState])

    # Back track through explored table to get the path
    path.append(goal_state_id)
    goal_state_id = explored_table.get(goal_state_id, "")
    while goal_state_id != "":
        path.append(goal_state_id)
        goal_state_id = explored_table.get(goal_state_id, "")
    # reverse path so it goes start to goal
    path.reverse();
    # validate path
    if path[0] == start_state_id:
        return path, states_explored
    return None, None


# Returns unique state identifier
def serialize(state_array):
    return ''.join(state_array)


# Marks a state as visited and checks if it has already been visited.
# Returns False if previously visited a true if first visit
def mark_state_visited(state_id, parent_state_id, explored_table):
    # python dictionaries are a hash table implementation
    # checking existence of state is only O(1)
    if state_id in explored_table:
        # print("Possible cycle detected. State Id:", stateId, "already added.")
        return False
    else:
        # table is childNode->parentNode
        # important for final path lookup
        explored_table[state_id] = parent_state_id;
    return True


# Check if the start state is valid.
# Returns true if valid.
def get_board_context(start_state_id):
    row_table = {}
    if type(start_state_id) is not list:
        print("Error: initial state is not a list.")
        return None
    n_row0 = len(start_state_id[0])
    if n_row0 < 4:
        print("Error: first row must be at least width 4.")
        return None
    # depth maximum
    d_max = n_row0 - 2
    n_row_last = n_row0 + 1
    position = 0
    for i in range(d_max, -1, -1):
        n_row_last = n_row_last - 1
        for j in range(0, n_row_last):
            row_table[position] = i
            position = position + 1
    n_row_last = 2
    n = -1 * d_max - 1
    for i in range(-1, n, -1):
        n_row_last = n_row_last + 1
        for j in range(0, n_row_last):
            row_table[position] = i
            position = position + 1
    positions_max = n_row0 * n_row0 + n_row0 - 4
    if positions_max != position:
        print("Error: expected", positions_max, "positions, but got", position, ".")
        return None
    return n_row0, row_table


# Check win state
# @return false if no winner else returns 'w' or 'b' depending on who won
def checkWinBoard(current_state):
    # Check all the 'w' pieces have been removed from the board
    if current_state.find('w') == -1:
        return 'b'
    elif current_state.find('b') == -1:
        return 'w'
    # both 'w' and 'b' pieces are known to exist
    if current_state[16] == 'X' and current_state[17] == 'X':
        return True
    return False


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
# Generate the possible states from available moves.
# Wasted CPU cycles visiting each cell on the board.
# Iterating through pieces would be more efficient,
# but saving piece.name => cellPosition uses more memory
def movegen(current_state_array, side):
    new_state_list = []
    return new_state_list


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
# @return row
def pos_to_row(pos, width):
    rows_tot = width_to_rows_tot(width)
    pos_tot = width_to_pos_tot(width)
    pos_mid = pos_tot / 2 - 1
    # row_depth is the row number from the shortest row
    # negative goes upward and positive down
    # this mathematical series calculation below has
    # has only been tested with width < 6
    if pos <= pos_mid+1:
        row_depth_float = (((-1 + math.sqrt(8 * pos_mid - 8 * pos + 25)) / 2) - 2) * -1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        # but is sufficient for this assignment
        row_pos = math.ceil((row_depth_float - row_depth) * row_width)
    else:
        row_depth_float = ((-1+math.sqrt(8*pos-8*pos_mid+9))/2)-1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        row_pos = math.floor((row_depth_float - row_depth) * row_width)
    # width of the row
    row = int(row_depth + (rows_tot-1)/2)
    return row, row_pos, row_width


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
def print_state(state_id, pos_row_table):
    pos_tot = len(state_id)
    width = pos_tot_to_width(pos_tot)
    rows_tot = width_to_rows_tot(width)
    row, row_pos = pos_to_row(pos, width)
    print('-' * 5 * rows_tot)
    for pos in range(0, pos_tot):
        print(" |  ", end='')
        print(state_id[pos], end='')

    print('-' * 5 * rows_tot)


# writes the stateId to readable board to file
def write_state(fileHandle, stateId):
    for i in range(0, 36):
        fileHandle.write(stateId[i])
        if i % 6 == 5:
            fileHandle.write("\n")


# Writes the path of states to the console.
def printPath(path):
    n = len(path)
    for i in range(0, n):
        print_state(path[i])
        print("\n", end='')


# Writes the path of states to a file.
def write_path(fileHandle, path):
    n = len(path)
    for i in range(0, n):
        fileHandle.write("Move: " + str(i) + "\n")
        write_state(fileHandle, path[i])
        fileHandle.write("\n")


# FOR DEBUG USE
# writes the parent state board to a file
def debug_file_state(fileHandle, statePair, queue):
    fileHandle.write("==============================================\n")
    fileHandle.write("PriorityQueue.length = " + str(queue.qsize()) + "\n")
    fileHandle.write("Priority " + str(statePair[0]) + "\n")
    write_state(fileHandle, statePair[1].id)


# FOR DEBUG USE
# writes the child or successor state board to a file
def debug_file_child_state(fileHandle, statePair):
    fileHandle.write("CHILD Priority " + str(statePair[0]) + "\n")
    write_state(fileHandle, statePair[1].id)


oskaplayer(['wwww', '---', '--', '---', 'bbbb'], 'w', 2)
