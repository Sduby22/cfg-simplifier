from typing import Dict, List, Set


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
        self.P[A].add(b)
        self.T.update([ch for ch in b if ch not in self.N and ch != EPSILON])

    def simplyfy(self):
        self._remove_null()
        self._remove_unit()
        self._remove_useless()

    def _remove_null(self):
        # algorithm 3: epsilon elimination
        # step1: calculates all nullables
        nullable = [key for key in self.N if any(str == EPSILON for str in self.P[key])]
        # step2: replace nullable characters to \e|ch
        # step3: if S in nullables, add S'
        pass

    def _remove_unit(self):
        # algorithm 4: remove unit production 
        # Calculates all unit pairs of every character in N
        # replace X->Y Y->a to X->a
        pass

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
                self.P[key] = [item for item in self.P[key] if item not in remove_list]

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
                self.P[key] = [item for item in self.P[key] if item not in remove_list]

    def _remove_useless(self):
        # algorithm 1&2
        self._remove_not_generating()
        self._remove_unreachable()
