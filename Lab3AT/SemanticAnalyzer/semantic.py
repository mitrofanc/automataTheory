class SemanticAnalyzer:
    def __init__(self):
        self.scopes: list[dict] = [{}] # stack of scopes
        self.functions: dict = {} # TASK: name -> {'params': [...]}
        self.in_function: bool = False

    # current scope
    @property
    def cur(self) -> dict:
        return self.scopes[-1]

    def enter_scope(self):
        self.scopes.append({})

    def leave_scope(self):
        self.scopes.pop()

    def declare(self, name: str, info: dict):
        if name in self.cur:
            raise SemanticError(f"Variable '{name}' already declared in this scope")
        self.cur[name] = info

    def lookup(self, name: str) -> dict:
        if self.in_function:
            if name in self.cur:
                return self.cur[name]
            raise SemanticError(f"Variable '{name}' not declared in function scope")

        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variable '{name}' not declared")

    def analyze(self, node):
        nodetype = node[0]
        method = getattr(self, f'analyze_{nodetype}', self.generic_analyze)
        return method(node)

    def generic_analyze(self, node):
        raise SemanticError(f"No semantic rule for node type {node[0]}")

    def literal_type(self, node):
        v = node[1]
        return 'bool' if isinstance(v, bool) else 'int'

    def check_dimensions(self, name: str, dims: list):
        for d in dims:
            if self.analyze(d) != 'int':
                raise SemanticError(f"Dimension in '{name}' must be integer")
            if d[0] == 'literal' and d[1] <= 0:
                raise SemanticError(f"Dimension in '{name}' must be positive")

    def analyze_var_declaration(self, node):
        _, name, dims, lit = node
        self.check_dimensions(name, dims)
        self.declare(name, {
            'type': self.literal_type(lit),
            'dimensions': dims
        })

    # name = expr
    def analyze_assignment(self, node):
        _, name, expr = node
        var = self.lookup(name)
        expr_type = self.analyze(expr)
        if var['type'] != expr_type:
            raise SemanticError(f"Type mismatch on assignment to '{name}'")

    def analyze_binop(self, node):
        _, op, l, r = node
        lt, rt = self.analyze(l), self.analyze(r)
        if op in ['+', '-', '*', '/']:
            if (lt, rt) != ('int', 'int'):
                raise SemanticError(f"Operator '{op}' needs integer operands")
            return 'int'
        if op == 'AND':
            if (lt, rt) != ('bool', 'bool'):
                raise SemanticError("Operator AND needs boolean operands")
            return 'bool'
        return None

    def analyze_literal(self, node):
        return self.literal_type(node)

    def analyze_expression(self, node):
        val = node[1]
        if isinstance(val, str):
            return self.lookup(val)['type']
        return self.analyze(val)

    # SIZE(name)
    def analyze_size_operator(self, node):
        _, name = node
        self.lookup(name)
        return 'int'

    # REDUCE/EXTEND
    def analyze_size_change(self, node):
        _, op, name, dims = node
        self.lookup(name)
        self.check_dimensions(name, dims)
        return 'int'

    # name[d1,d2,...]
    def analyze_array_access(self, node):
        _, name, idx = node
        info = self.lookup(name)
        if len(idx) != len(info['dimensions']):
            raise SemanticError(f"Index count mismatch for '{name}'")
        for d in idx:
            if self.analyze(d) != 'int':
                raise SemanticError(f"Index for '{name}' must be integer")
        return info['type']

    # NOT
    def analyze_not(self, node):
        if self.analyze(node[1]) != 'bool':
            raise SemanticError("NOT requires boolean operand")
        return 'bool'

    # AND
    def analyze_and(self, node):
        return self.analyze_binop(node)

    # MXTRUE/MXFALSE
    def analyze_mxtrue(self, node):
        return self.analyze_not(node)

    # MXFALSE
    def analyze_mxfalse(self, node):
        return self.analyze_not(node)

    def analyze_comparison_zero(self, node):
        _, op, expr = node
        if self.analyze(expr) != 'int':
            raise SemanticError(f"{op} requires integer operand")
        return 'bool'

    # FOR counter BOUNDARY expr STEP counter2 block
    def analyze_for_loop(self, node):
        _, ctr, bound, step, body = node
        if self.lookup(ctr)['type'] != 'int' or self.lookup(step)['type'] != 'int':
            raise SemanticError("Loop var and step must be integer")
        self.analyze(bound)
        for st in body:
            self.analyze(st)

    # SWITCH expr TRUE/FALSE block [FALSE/TRUE block]
    def analyze_switch(self, node):
        _, cond, choice, block, elseblock = node
        if self.analyze(cond) != 'bool':
            raise SemanticError("Switch condition must be boolean")
        for st in block: self.analyze(st)
        if elseblock:
            for st in elseblock[1]: self.analyze(st)

    def analyze_move(self, node):
        return None

    def analyze_rotate_left(self, node):
        return None

    def analyze_rotate_right(self, node):
        return None

    def analyze_get_environment(self, node):
        return 'bool'

    # TASK name params block RESULT var
    def analyze_task_function(self, node):
        _, fname, params, body, ret = node
        if len(self.scopes) != 1 or self.scopes[-1] is not self.scopes[0]:
            raise SemanticError("TASK can only be declared at global scope")

        if fname in self.functions:
            raise SemanticError(f"Function '{fname}' already declared")

        self.functions[fname] = {'params': params}

        self.enter_scope()
        for p in params:
            self.declare(p, {'type': 'unknown', 'dimensions': []})

        for stmt in body:
            self.analyze(stmt)

        if ret[0] != 'return':
            raise SemanticError("Missing RESULT in function")

        self.leave_scope()

    # DO name(args)
    def analyze_function_call(self, node):
        _, fname, args = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")

        sig = self.functions[fname]['params']
        if len(args) != len(sig):
            raise SemanticError(f"Argument count mismatch in call '{fname}'")
        for a in args:
            self.analyze(a)

    # GET name (result)
    def analyze_get_function_result(self, node):
        _, fname = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")

class SemanticError(Exception):
    pass
