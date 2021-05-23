import re
from cfg import *


def epsilonify(str):
    return str.replace(r'\e', EPSILON).replace('ϵ', EPSILON).replace('ε', EPSILON)

def exception_search(pattern, string):
    res = re.search(pattern, string)
    if not res:
        raise Exception(f'Does not match pattern {pattern}')
    return res

def readCFG(filepath):
    lines=[]
    with open(filepath, 'r', encoding='utf8') as f:
        lines=list(map(lambda x: epsilonify(x.strip().replace(' ', '')),
                           f.readlines()))
    cfg = CFG()
    for index in range(len(lines)):
        try:
            x = lines[index]
            if index == 0:
                # read N
                nline = exception_search(r'N=\[(.*)\]', x).group(1)
                cfg.N = set(nline.split(','))
            elif index == 1:
                # read S
                sline = exception_search(r'S=(\S)', x).group(1)
                cfg.S = sline
            else:
                # read P
                if x:
                    pline = exception_search(r'(\S+)->(\S+)', x)
                    for dst in pline.group(2).split('|'):
                        cfg.pushP(pline.group(1), dst)
        except Exception as e:
            print(f'parse failed at line {index+1}: {e}')
            exit(1)
    return cfg
