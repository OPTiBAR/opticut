from typing import Dict, List, Union
import pyomo.environ as pyo
from itertools import compress

# pyo.SolverFactory('glpk').available()

# class BarError(ValueError):


def solve(
        pieces: Dict[int,int],
        bars: Dict[int, Union[None,int]] = None,
        std_bar: int = None,
        blade_width: int = 0,
        pattern_num: int = None,
        blade_num: int = None
    ) -> Dict:
    """solves 

    Args:
        pieces (Dict[int,int]): dict of pieces and their corresponding numbers.
        bars (Dict[int, Union[None,int]], optional): dict of the available bars and their corresponding numbers. If the specified number is None there is no limit. Defaults to None.
        std_bar (int, optional): standard length of the bar. Just one of the bars and std_bar should be given. Defaults to None.
        blade_width (int, optional): the width of the cutting blade. Defaults to 0.
        pattern_num (int, optional): maximum number of the used patterns and if is None there is no limit. Defaults to None.
        blade_num (int, optional): maximum number of the cutting blades and if is None there is no limit. Defaults to None.

    Returns:
        Dict: _description_
    """
    pass