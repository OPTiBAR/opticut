from typing import Dict, List, Tuple, NamedTuple, Union
import pyomo.environ as pyo
import math

class IntegerLengthError(TypeError):
    def __init__(self, *args: object) -> None:
        super().__init__('All lengths should be integer.')

class UnlimitedBarError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__('There Should be an unlimited bar with a length that all the pieces can be cut from.')

class Pattern():
    def __init__(self, length : int, pieces: Dict[int,int] ) -> None:
        self.length = length
        self.pieces = pieces
    def __repr__(self) -> str:
        return f"\nPattern: \n\tLength: {self.length}\n\tPieces: {self.pieces}\n"

class CG():
    """Column Generation algorithm for cutting stock problem
    """
    def __init__(self, solver: pyo.SolverFactory,
            pieces: Dict[int,int],
            bars: Dict[int,int],
            blade_width: int = 0,
            pattern_num: int = -1,
            blade_num: int = -1
        ) -> None:
        # validate inputs
        if not CG._validate_len_integrality(pieces) or not CG._validate_len_integrality(bars):
            raise IntegerLengthError()
        if not CG._validate_feasibility(bars, pieces, blade_width):
            raise UnlimitedBarError()
        self.solver = solver
        self.pieces = pieces
        self.bars = bars
        self.blade_width = blade_width
        self.pattern_num = pattern_num
        self.blade_num = blade_num
    
    @staticmethod
    def _validate_len_integrality(d:Dict[int,int])-> bool:
        for length in d:
            if not isinstance(length,int):
                return False
        return True

    @staticmethod        
    def _validate_feasibility(bars, pieces, blade_width)-> bool:
        unlimited_lengths = list(filter(lambda length: bars[length] == -1, bars))
        if len(unlimited_lengths) == 0:
            return False
        bar_len = max(unlimited_lengths) # find longest unlimited bar
        for length in pieces:
            if not(length == bar_len or length <= (bar_len - blade_width)):
                return False
        return True

    def solve(self) -> Dict[Pattern, int]:
        initial_patterns = self._get_initial_patterns()
        parent = Parent(self.solver, pieces=self.pieces, initial_patterns=initial_patterns, pattern_num=self.pattern_num, bars= self.bars)
        child = Child(solver=self.solver, lengths=list(self.pieces.keys()), blade_width=self.blade_width, blade_num=self.blade_num)
        
        while True:
            parent.solve(domain=pyo.NonNegativeReals)
            for bar_length in self.bars.keys():
                child.solve(bar_length=bar_length, duals=parent.get_duals()['pieces'])
                if bar_length - parent.get_duals()['bars'].get(bar_length,0) - child.get_obj() < - 1e-4:
                    parent.add_pattern(child.get_pattern())
                    break # for loop
            else:
                break # while loop
        parent.solve(domain=pyo.NonNegativeIntegers)
        results = {}
        for pattern, num in parent.get_values().items():
            if int(num) != 0:
                results[pattern] = int(num)
        return results

    def _get_initial_patterns(self) -> List[Pattern]:
        patterns = []
        bar_len = max(filter(lambda length: self.bars[length] == -1, self.bars)) # find longest unlimited bar
        for piece_len in self.pieces.keys():
            patterns.append(Pattern(bar_len, {piece_len:1})) # math.floor(bar_len/piece_len)
        return patterns

class Parent():
    def __init__(self, solver: pyo.SolverFactory, pieces: Dict[int,int], initial_patterns: List[Pattern], pattern_num: int, bars:Dict[int, int]) -> None:
        self.solver = solver
        self.patterns = initial_patterns
        self.pieces = pieces
        self.results = {'values': {}, 'obj': None, 'duals': None}
        self.pattern_num = pattern_num
        self.bars = bars

    def solve(self, domain):
        model = pyo.ConcreteModel()
        model.x = pyo.Var(self.patterns, within=domain)

        # initialize the x variables
        if domain == pyo.NonNegativeReals:
            for pattern,value in self.get_values().items():
                model.x[pattern] = value

        def bars_rule(model,length):
            if self.bars[length] != -1:
                ptrns = list(filter(lambda p: p.length==length, self.patterns))     
                if len(ptrns) == 0:
                    return pyo.Constraint.Skip
                return sum(model.x[p] for p in ptrns) <= self.bars[length]
            else:
                return pyo.Constraint.Skip
        model.bars_rule = pyo.Constraint(self.bars.keys(), rule=bars_rule)

        def pieces_rule(model,length):
            return sum(model.x[p] * p.pieces.get(length,0) for p in self.patterns) >= self.pieces[length]
        model.pieces_rule = pyo.Constraint(self.pieces.keys(), rule=pieces_rule)
        model.obj = pyo.Objective(expr=sum(model.x[p] * p.length for p in self.patterns))

        if domain == pyo.NonNegativeIntegers and (self.pattern_num != -1):
            model.y = pyo.Var(self.patterns, domain=pyo.Binary)
            def used_rule(model,pattern):
                return model.x[pattern] <= model.y[pattern] * max([math.ceil(self.pieces[l]/pattern.pieces[l]) for l in pattern.pieces.keys()])
            model.used_rule = pyo.Constraint(self.patterns, rule=used_rule)
            def max_rule(model):
                return sum(model.y[p] for p in self.patterns) <= self.pattern_num
            model.max_rule = pyo.Constraint(rule=max_rule)
        
        model.dual = pyo.Suffix(direction= pyo.Suffix.IMPORT)
        r = self.solver.solve(model)
        # print(r.solver.termination_condition)
        results = {
            'values': {p:pyo.value(model.x[p]) for p in self.patterns},
            'obj': pyo.value(model.obj),
        }
        if domain == pyo.NonNegativeReals:
            results['duals'] = {
                'pieces': {length:model.dual[model.pieces_rule[length]] for length in model.pieces_rule},
                'bars': {length:model.dual[model.bars_rule[length]] for length in model.bars_rule},
            }
        self.results = results
    
    def get_duals(self) -> Dict[int,float]:
        return self.results['duals']
    
    def get_values(self):
        return self.results['values']

    def add_pattern(self, pattern: Pattern):
        self.patterns.append(pattern)


class Child():
    def __init__(self, solver: pyo.SolverFactory, lengths: List[int], blade_width: int, blade_num: int) -> None:
        self.solver = solver
        self.lengths = lengths
        self.blade_width = blade_width
        self.blade_num = blade_num
        self.results = {}
    
    def solve(self, duals:Dict[int,float], bar_length: int)-> None:
        model = pyo.ConcreteModel()
        model.z = pyo.Var(self.lengths, within=pyo.NonNegativeIntegers)
        model.s = pyo.Var(within=pyo.NonNegativeReals)
        model.w = pyo.Var(within=pyo.Binary)

        def capacity_rule(model):
            return sum(model.z[l]*l for l in self.lengths) == bar_length - model.s - (sum(model.z[l] for l in self.lengths)-1+model.w) * self.blade_width
        model.capacity_rule = pyo.Constraint(rule=capacity_rule)
        def slack_lower_rule(model):
            return (model.s / bar_length) <= model.w
        def slack_upper_rule(model):
            return model.w <= model.s

        model.slack_lower_rule = pyo.Constraint(rule=slack_lower_rule)
        model.slack_upper_rule = pyo.Constraint(rule=slack_upper_rule)
        if self.blade_num != -1:
            def blade_num_rule(model):
                return sum(model.z[l] for l in self.lengths) <= self.blade_num + 1 - model.w
            model.blade_num_rule = pyo.Constraint(rule=blade_num_rule)
  
        model.obj = pyo.Objective(expr=sum(model.z[l]*duals[l] for l in self.lengths),sense=pyo.maximize)
        
        self.solver.solve(model)
        self.results = {
            "obj":pyo.value(model.obj) ,
            "pattern": Pattern(bar_length, {length: int(pyo.value(model.z[length])) for length in self.lengths if int(pyo.value(model.z[length])) > 0}),
        }
    
    def get_obj(self) -> float:
        return self.results['obj']
    
    def get_pattern(self) -> Pattern:
        return self.results['pattern']



    