from typing import Dict, List, Union, NamedTuple
import pyomo.environ as pyo

class Pattern(NamedTuple):
    length : int
    pieces: Dict[int,int]

class Algorithm():
    def __init__(self, solver: pyo.SolverFactory,
            pieces: Dict[int,int],
            bars: Dict[int, Union[None,int]] = None,
            std_bar: int = None,
            blade_width: int = 0,
            pattern_num: int = None,
            blade_num: int = None) -> None:
        pass
    def solve(self):
        return 


class Parent():
    def __init__(self, solver: pyo.SolverFactory, pieces: Dict[int,int], initial_paterns: List[Pattern]) -> None:
        self.solver = solver
    

        

class Child():
    def __init__(self, solver: pyo.SolverFactory, lengths: List[int], blade_width: int, blade_num: Union[int,None]) -> None:
        self.solver = solver
        self.blade_width = blade_width
        self.blade_num = blade_num

    