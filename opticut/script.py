from typing import Dict, List, Union
import pyomo.environ as pyo

class SolverError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    

class CuttingStock():
    def __init__(self, solver_name:str='glpk') -> None:
        if not pyo.SolverFactory(solver_name).available():
            raise SolverError(solver_name)
        else:
            self.solver = pyo.SolverFactory(solver_name)


    def solve(
            pieces: Dict[int,int],
            bars: Dict[int, Union[None,int]] = None,
            std_bar: int = None,
            blade_width: int = 0,
            pattern_num: int = None,
            blade_num: int = None
        ) -> Dict: 
        """_summary_

        :param pieces: dict of pieces' length and their corresponding number.
        :type pieces: Dict[int,int]
        :param bars: dict of the available bars' length and their corresponding number, If the specified number is None there is no limit. defaults to None
        :type bars: Dict[int, Union[None,int]], optional
        :param std_bar: _description_, defaults to None
        :type std_bar: int, optional
        :param blade_width: _description_, defaults to 0
        :type blade_width: int, optional
        :param pattern_num: _description_, defaults to None
        :type pattern_num: int, optional
        :param blade_num: _description_, defaults to None
        :type blade_num: int, optional
        :return: _description_
        :rtype: Dict
        """    
        

        pass


    # """solves 

    # Args:
    #     :param pieces (Dict[int,int]): dict of pieces and their corresponding numbers.
    #     :param bars (Dict[int, Union[None,int]], optional): dict of the available bars' length and their corresponding number. If the specified number is None there is no limit. Defaults to None.
    #     :param std_bar (int, optional): standard length of the bar. Just one of the bars and std_bar should be given. Defaults to None.
    #     :param blade_width (int, optional): the width of the cutting blade. Defaults to 0.
    #     :param pattern_num (int, optional): maximum number of the used patterns and if is None there is no limit. Defaults to None.
    #     :param blade_num (int, optional): maximum number of the cutting blades and if is None there is no limit. Defaults to None.

    # Returns:
    #     Dict: _description_

    # """