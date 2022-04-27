from typing import Dict, List, Tuple
import pyomo.environ as pyo
import click
import json
from optimization import CG, Pattern


class SolverError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
        cg.solve()



@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.option('--blade-width', help="blade's width")
@click.option('--blade-num', help='maximum number of blades')
@click.option('--pattern-num', help='maximum number of used patterns')
@click.option('--solver-name', default='glpk', help='name of the solver in lowercase')
def cli(input, output, blade_width, blade_num, pattern_num, solver_name):
    """Copy contents of INPUT to OUTPUT."""
    cli_options = {
        'blade_width' : blade_width,
        'blade_num' : blade_num,
        'pattern_num' : pattern_num,
    }
    input_data = json.load(input)
    data = {}
    for item in ('pieces', 'bars'): 
        data[item] = {p['length']:p['quantity'] for p in input_data[item]}

    input_options = input_data.get('options', {})

    options = {}
    for option in cli_options:
        if cli_options[option] is not None:
            options[option] = cli_options[option]
        elif option in input_options:
            options[option] = input_options[option]
    cs = CuttingStock(solver_name)
    cs.solve(**data, **options)

if __name__ == '__main__':
    cli()
