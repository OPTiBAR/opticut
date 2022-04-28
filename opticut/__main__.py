import click
import json
from opticut.cs import CuttingStock

@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))
@click.option('--blade-width', help="blade's width", type=int)
@click.option('--blade-num', help='maximum number of blades', type=int)
@click.option('--pattern-num', help='maximum number of used patterns', type=int)
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
    print(cs.solve(**data, **options))

if __name__ == '__main__':
    cli()
