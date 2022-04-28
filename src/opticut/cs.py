from typing import Dict, List, Tuple
import pyomo.environ as pyo
from opticut.optimization import CG, Pattern

class SolverError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__('the solver is not available')

class CuttingStock():
    def __init__(self, solver_name:str) -> None:
        if not pyo.SolverFactory(solver_name).available():
            raise SolverError(solver_name)
        else:
            self.solver = pyo.SolverFactory(solver_name)

    def solve(self,
            pieces: Dict[int,int],
            bars: Dict[int, int],
            blade_width: int = 0,
            pattern_num: int = -1,
            blade_num: int = -1
        ) -> List[Tuple[Pattern,int]]:
        """_summary_

        :param pieces: Dict of pieces' length and their corresponding number. Lengths should be integer.
        :type pieces: Dict[int,int]
        :param bars: Dict of the available bars' length and their corresponding number. Lengths should be integer.
        :type bars: Dict[int, int]
        :param blade_width: The width of the cutting blade, defaults to 0.
        :type blade_width: int, optional
        :param pattern_num: maximum number of the used patterns and if is -1 there is no limit, defaults to -1.
        :type pattern_num: int, optional
        :param blade_num: maximum number of the cutting blades and if is -1 there is no limit, defaults to -1.
        :type blade_num: int, optional
        :return: _description_
        :rtype: Dict
        """
        cg = CG(self.solver, pieces, bars, blade_width, pattern_num, blade_num)
        res = cg.solve()
        # pl = {}
        # for pattern,pn in res.items():
        #     for length,ln in pattern.pieces.items():
        #         pl[length] = pl.get(length,0) + ln * pn
        # print(pl)
        # print(pieces)
        return(res)
