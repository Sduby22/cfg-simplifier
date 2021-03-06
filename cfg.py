from typing import Dict, List, Set
from functools import reduce


EPSILON = 'ε'
class CFG:
    def __init__(self, N=[], T=[], P={}, S=''):
        self.P: Dict[str, Set[str]]
        self.N: Set[str]
        self.T: Set[str]
        self.S: str
        self.N = set(N)
        self.T = set(T)
        self.P = P
        self.S = S

    def print(self):
        print(f'N: {self.N}')
        print(f'T: {self.T}')
        print(f'S: {self.S}')
        self._printP()

    def _printP(self):
        print('P:')
        for n in self.N:
            dst=''
            for p in self.P[n]:
                dst+=f'|{p}' if dst else p
            if dst:
                print(f'\t{n}->{dst}')

    def pushP(self, A='', b=''):
        if(len(A) != 1):
            raise RuntimeError('Multiple Characters before "->"')
        if(A not in self.N):
            raise RuntimeError(f'{A} is not in N.')
        if(A not in self.P):
            self.P[A] = set([])
        if b:
            self.P[A].add(b)
            self.T.update([ch for ch in b if ch not in self.N and ch != EPSILON])

    def simplyfy(self):
        self._remove_null()
        self._remove_unit()
        self._remove_useless()

    def _remove_useless(self):
        # algorithm 1&2
        self._remove_not_generating()
        self._remove_unreachable()

    def _remove_null(self):
        # algorithm 3: epsilon elimination
        # step1: calculates all nullables
        nullables = set([key for key in self.N if any(str == EPSILON for str in self.P[key])])
        all_null = lambda x: all(ch in nullables or ch == EPSILON for ch in x)
        new_nullables = set(nullables)
        while new_nullables:
            nullables.update(new_nullables)
            new_nullables = [key for key in self.N - nullables if any(all_null(x) for x in self.P[key])]

        # step2: replace nullable characters to \e|ch
        for key in self.N:
            pending=set([])
            remove_list = []
            for dst_str in self.P[key]:
                nullable_map = [(index, dst_str[index]) for index in range(len(dst_str)) if dst_str[index] in nullables]
                for x in range(2 ** len(nullable_map) - 1):
                    binstr = bin(x)[2:].rjust(len(nullable_map), '0')
                    new_str = list(dst_str)
                    for bin_index in range(len(nullable_map)):
                        index, ch = nullable_map[bin_index]
                        new_str[index] = ch if binstr[bin_index] == '1' else EPSILON
                        if not all(ch == EPSILON for ch in dst_str):
                            pending.add(''.join(new_str).replace(EPSILON, ''))
                if all(ch == EPSILON for ch in dst_str):
                    remove_list.append(dst_str)
            list(map(lambda x: self.P[key].remove(x), remove_list))
            list(map(lambda x: self.pushP(key, x), pending))

        # step3: if S in nullables, add S'
        if self.S in nullables:
            self.S = 'X'
            self.N.add('X')
            self.pushP('X', EPSILON)
            self.pushP('X', 'S')
        pass

    def _remove_unit(self):
        # algorithm 4: remove unit production 
        # Calculates all unit pairs of every character in N
        unit_pairs: Dict[str, Set[str]]
        unit_pairs = {}
        def get_pairs_one_step(n) -> Set[str]:
            if n in unit_pairs:
                return unit_pairs[n]
            pairs = set([n])
            units = [item for item in self.P[n] if item in self.N]
            pairs.update(units)
            return pairs
        def get_pairs_recursive(n, iterlist) -> Set[str]:
            iterlist.append(n)
            if n in unit_pairs:
                return unit_pairs[n]
            pairs = get_pairs_one_step(n)
            pairs_list = [get_pairs_recursive(item, list(iterlist)) for item in pairs if item != n and item not in iterlist]
            list(map(lambda x: pairs.update(x), pairs_list))
            unit_pairs[n] = pairs
            return pairs
        for n in self.N:
            get_pairs_recursive(n,[])

        # replace X->Y Y->a to X->a
        def get_non_unit_productions(n):
            return [production for production in self.P[n] if production not in self.N]
        non_unit_dict: Dict[str, Set[str]]
        non_unit_dict = {}
        for x in self.N:
            non_unit_dict[x] = get_non_unit_productions(x)
        for x in self.N:
            new_p = set(non_unit_dict[x])   # non unit of x
            for y in unit_pairs[x]:
                new_p.update(non_unit_dict[y]) # non unit of unit pairs of x
            self.P[x] = new_p

    def _remove_not_generating(self):
        # algorithm 1: remove non generating symbols
        # begin with terminate characters
        generating = set(self.T)
        non_generating = set(self.N) - set(generating)

        appended = True
        while appended:
            appended = False
            for n in non_generating:
                for p in self.P[n]:
                    if all(x in generating for x in p):
                        generating.add(n)
                        appended = True
                        break
            non_generating = set(self.N) - set(generating)

        # delete non generating symbols
        for n in non_generating:
            self.N.remove(n)
            self.P.pop(n)
            for key in self.N:
                remove_list = [str for str in self.P[key] if any(x == n for x in str)]
                self.P[key] = set([item for item in self.P[key] if item not in remove_list])

    def _remove_unreachable(self):
        # algorithm 2: remove unreachable symbols
        # begin with S
        reachable = set([self.S])
        unreachable = set(self.N) - set(reachable)

        appended = True
        while appended:
            appended = False
            pending=set([])
            for n in reachable:
                for str in self.P[n]:
                    for ch in str:
                        if ch in unreachable:
                            pending.add(ch)
                            unreachable.remove(ch)
                            appended = True
            reachable.update(pending)

        # delete unreachable symbols
        for n in unreachable:
            self.N.remove(n)
            self.P.pop(n)
            for key in self.N:
                remove_list = [str for str in self.P[key] if any(x == n for x in str)]
                self.P[key] = set([item for item in self.P[key] if item not in remove_list])

