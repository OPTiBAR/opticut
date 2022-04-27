from typing import Dict, List, Tuple, NamedTuple
import pyomo.environ as pyo
import math


class Pattern():
    def __init__(self, length : int, pieces: Dict[int,int] ) -> None:
        self.length = length
        self.pieces = pieces

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
        self.solver = solver
        self.pieces = pieces
        self.bars = bars
        self.blade_width = blade_width
        self.pattern_num = pattern_num
        self.blade_num = blade_num
        
    def solve(self) -> List[Tuple[Pattern, int]]:
        initial_patterns = self._get_initial_patterns()
        parent = Parent(self.solver, pieces=self.pieces, initial_patterns=initial_patterns, pattern_num=self.pattern_num, bars= self.bars)
        child = Child(solver=self.solver, lengths=list(self.pieces.keys()), blade_width=self.blade_width, blade_num=self.blade_num)
        
        while True:
            parent.solve(domain=pyo.NonNegativeReals)
            for bar_length in self.bars.keys():
                result = child.solve(bar_length=bar_length, duals=parent.get_duals())
                if bar_length - result['obj'] > 1e-4:
                    parent.add_pattern(result['pattern'])
                    break # for loop
            else:
                break # while loop
        parent.solve(domain=pyo.NonNegativeIntegers)
        return parent.get_values()

    def _get_initial_patterns(self) -> List[Pattern]:
        patterns = []
        print(self.bars)
        bar_len = max(filter(lambda length: self.bars[length] == -1, self.bars)) # find longest unlimited bar
        for piece_len in self.pieces.keys():
            patterns.append(Pattern(bar_len, {piece_len:math.floor(bar_len/piece_len)}))
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
        for pattern,value in self.get_values().items():
            model.x[pattern] = value

        def bar_rule(model,length):
            if self.bars[length] != -1:
                ptrns = list(filter(lambda p: p.length==length, self.patterns))     
                if len(ptrns) == 0:
                    return pyo.Constraint.Skip
                return sum(model.x[p] for p in ptrns) <= self.bars[length]
            else:
                return pyo.Constraint.Skip
        model.bar_rule = pyo.Constraint(self.bars.keys(), rule=bar_rule)

        def pieces_rule(model,length):
            return sum(model.x[p] * p.pieces.get(length,0) for p in self.patterns) >= self.pieces[length]
        model.pieces_rule = pyo.Constraint(self.pieces.keys(), rule=pieces_rule)
        model.obj = pyo.Objective(expr=sum(model.x[p] * p.length for p in self.patterns))

        if domain == pyo.NonNegativeIntegers and (self.pattern_num != -1):
            model.y = pyo.Var(self.patterns, domain=pyo.Binary)
            def used_rule(model,pattern):
                return model.x[pattern] <= model.y[pattern] * max([self.pieces[l]/pattern.pieces[l] for l in pattern.pieces.keys()])
            model.used_rule = pyo.Constraint(self.patterns, rule=used_rule)
            def max_rule(model):
                return sum(model.y[p] for p in self.patterns) <= self.pattern_num
            model.max_rule = pyo.Constraint(rule=max_rule)

        model.dual = pyo.Suffix(direction= pyo.Suffix.IMPORT)
        self.solver.solve(model)
        results = {
            'values': [(p,pyo.value(model.x[p])) for p in self.patterns],
            'obj': pyo.value(model.obj),
        }
        if domain == pyo.NonNegativeReals:
            results['duals'] = {length:model.dual[model.pieces_rule[length]] for length in model.pieces_rule}
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
    
    def solve(self, duals:Dict[int,float], bar_length: int):
        model = pyo.ConcreteModel()
        model.z = pyo.Var(self.lengths, within=pyo.NonNegativeIntegers)
        model.s = pyo.Var(within=pyo.NonNegativeReals)
        model.w = pyo.Var(within=pyo.Binary)

        def capacity_rule(model):
            return sum(model.z[l]*self.lengths[l] for l in self.lengths) == bar_length - model.s - (sum(model.z[l] for l in self.lengths)-1+model.w) * self.blade_width
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
        return {
            "obj":pyo.value(model.obj) ,
            "pattern": {length: int(pyo.value(model.x[length])) for length in self.lengths if int(pyo.value(model.x[length])) > 0},
        }



    