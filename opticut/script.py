from typing import Dict, List, Union
import pyomo.environ as pyo

class SolverError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    

class CuttingStock():
    def __init__(self, solver_name:str) -> None:
        if not pyo.SolverFactory(solver_name).available():
            raise SolverError(solver_name)
        else:
            self.solver = pyo.SolverFactory(solver_name)


    def solve(
            pieces: Dict[int,int],
            bars: Dict[int, Union[None,int]] = None,
            std_bar: Union[None,int] = None,
            blade_width: int = 0,
            pattern_num: Union[None,int] = None,
            blade_num: Union[None,int] = None
        ) -> Dict: 
        """_summary_

        :param pieces: dict of pieces' length and their corresponding number.
        :type pieces: Dict[int,int]
        :param bars: dict of the available bars' length and their corresponding number, If the specified number is None there is no limit. defaults to None
        :type bars: Dict[int, Union[None,int]], optional
        :param std_bar: tandard length of the bar. Just one of the bars and std_bar should be given, defaults to None
        :type std_bar: int, optional
        :param blade_width:  the width of the cutting blade, defaults to 0
        :type blade_width: int, optional
        :param pattern_num: maximum number of the used patterns and if is None there is no limit, defaults to None
        :type pattern_num: int, optional
        :param blade_num:  maximum number of the cutting blades and if is None there is no limit, defaults to None
        :type blade_num: int, optional
        :return: _description_
        :rtype: Dict
        """    
        

        pass

