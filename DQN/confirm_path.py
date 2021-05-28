import sys
sys.path.append('./learn')
from generateMap import generateMap
import numpy as np

generateMapClass = generateMap()
MAP = generateMapClass.sendMap
line = generateMapClass.line

FIELD_DICTS = {'S': 0.01, 'G': 99.0, 'U': -1.0}
MIN = 9999999999

aa = np.zeros((line, line), dtype=float) 
bb = np.zeros((line, line), dtype=float) 

path = []
all_paths = []

def _find_pos(field_type):
    return np.array(list(zip(*np.where(
    MAP == FIELD_DICTS[field_type]
))))

def _start_state():
    return _find_pos('S')[0]

def _end_state():
    return _find_pos('G')[0]


def dfs(start,end,maze,step):
    global path

    if start == end:
        all_paths.append(path[:])
        
        global MIN
        if(step < MIN):
            MIN = step
        return 0
    
    for action in range(0,line):
        next_action =  action
        next_state = [start, next_action]

        if next_action < 0 or next_action > line:
            continue
        if aa[tuple(next_state)] != -1 and bb[tuple(next_state)] != -1:
            #print(start)
            path.append(next_state)
            bb[tuple(next_state)] = -1
            dfs(next_action, end, maze, step+1)
            bb[tuple(next_state)] = 0.1
            path.pop()
    return 0


def get_score(MAP, all_paths):
    score_map = MAP.copy()
    line_number = len(all_paths)
    new_MAP = -(np.ones((line_number + 2, line_number + 2), dtype=np.float))

    matrix_list = []
    for data in all_paths:
        start_score = 0
        end_score = 0
        start_score = score_map[tuple(data[0])]
        end_score = score_map[tuple(data[-1])]
        mid_score = 0
        for i in data[1:-1]:
            mid_score = mid_score + score_map[tuple(i)]
        matrix_line = [start_score, mid_score, end_score]
        matrix_list.append(matrix_line)
    
    for data in enumerate(matrix_list):
        new_MAP[tuple([0, 0])] = data[1][0]
        new_MAP[tuple([0, data[0] + 1])] = data[1][1]
        new_MAP[tuple([data[0] + 1, 0])] = 0
        new_MAP[tuple([data[0] + 1, line_number + 1])] = data[1][2]
        new_MAP[tuple([line_number + 1, data[0] + 1])] = 0

    return new_MAP

if __name__ == '__main__':
    start_state = _start_state()
    end_state = _end_state()
    start = start_state[0]
    end = 0
    maze = MAP   
    
    aa = maze.copy()
    dfs(start,end,maze,0)
    bb[tuple(start_state)] = -1 
    result = get_score(maze, all_paths)
    np.save('./processdata/path_num.npy', len(result))
    np.savetxt('./processdata/newmap.txt', result)
    all_paths = np.array(all_paths, dtype=object)
    file_name="processdata/all_paths.npy"
    np.save("./"+file_name, all_paths)
    print("Attack matrix saved in 'DQN/{}'".format(file_name))
