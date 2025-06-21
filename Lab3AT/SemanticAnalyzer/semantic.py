class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.scopes: list[dict] = [{}]
        self.functions: dict = {}
        self.in_function: bool = False

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
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variable '{name}' not declared")

    def analyze(self, node):
        if isinstance(node, str):
            for scope in reversed(self.scopes):
                if node in scope:
                    return scope[node]['type']
            return 'int'

        if isinstance(node, bool):
            return 'bool'
        if isinstance(node, int):
            return 'int'

        if isinstance(node, list):
            for n in node:
                if isinstance(n, tuple) and n[0] == 'task_function':
                    _, fname, params, _ = n
                    if fname not in self.functions:
                        self.functions[fname] = { 'params': params, 'defined': False }
            for n in node:
                self.analyze(n)
            return

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
            if isinstance(d, tuple) and d[0] == 'literal' and isinstance(d[1], int) and d[1] <= 0:
                raise SemanticError(f"Dimension in '{name}' must be positive")

    def analyze_var_declaration(self, node):
        _, name, dims, expr = node
        if isinstance(expr, tuple) and expr[0] == 'get_environment':
            if not dims:
                dims = [
                    ('literal', 3),
                    ('literal', 3),
                    ('literal', 2)
                ]

        self.check_dimensions(name, dims)
        expr_type = self.analyze(expr)
        self.declare(name, {
            'type': expr_type,
            'dimensions': dims
        })
        return expr_type

    def analyze_assignment(self, node):
        _, name, expr = node
        var = self.lookup(name)
        expr_type = self.analyze(expr)

        if var.get('type') == 'unknown':
            var['type'] = expr_type
            return expr_type

        if var['type'] != expr_type:
            raise SemanticError(f"Type mismatch on assignment to '{name}'")
        return expr_type

    def analyze_binop(self, node):
        _, op, left, right = node
        lt = self.analyze(left)
        rt = self.analyze(right)

        if lt == 'unknown':
            lt = 'int'
        if rt == 'unknown':
            rt = 'int'

        if op in ['+', '-', '*', '/']:
            if (lt, rt) != ('int', 'int'):
                raise SemanticError(f"Operator '{op}' needs integer operands")
            return 'int'

        if op == 'AND':
            if (lt, rt) != ('bool', 'bool'):
                raise SemanticError("Operator AND needs boolean operands")
            return 'bool'

        return None

    def analyze_not(self, node):
        if self.analyze(node[1]) != 'bool':
            raise SemanticError("NOT requires boolean operand")
        return 'bool'

    def analyze_and(self, node):
        return self.analyze_binop(node)

    def analyze_mxtrue(self, node):
        return self.analyze_not(node)

    def analyze_mxfalse(self, node):
        return self.analyze_not(node)

    def analyze_comparison_zero(self, node):
        _, op, expr = node
        if self.analyze(expr) != 'int':
            raise SemanticError(f"{op} requires integer operand")
        return 'bool'

    def analyze_elementwise_comparison_zero(self, node):
        _, op, expr = node
        if self.analyze(expr) != 'int':
            raise SemanticError(f"{op} requires integer operand")
        return 'bool'

    def analyze_literal(self, node):
        return self.literal_type(node)

    def analyze_expr(self, node):
        return self.analyze(node[1])

    def analyze_array_literal(self, node):
        _, elems = node
        if not elems:
            return 'int'
        base = self.analyze(elems[0])
        for e in elems[1:]:
            if self.analyze(e) != base:
                raise SemanticError("Array elements must have the same type")
        return base

    def analyze_size_operator(self, node):
        _, name = node
        self.lookup(name)
        return 'int'

    def analyze_type_conversion(self, node):
        _, op, name = node
        self.lookup(name)
        return 'int'

    def analyze_size_change(self, node):
        _, op, name, dims = node
        self.lookup(name)
        self.check_dimensions(name, dims)
        return 'int'

    def analyze_array_access(self, node):
        _, name, idx = node
        info = self.lookup(name)
        if len(idx) != len(info['dimensions']):
            raise SemanticError(f"Index count mismatch for '{name}'")
        for d in idx:
            if self.analyze(d) != 'int':
                raise SemanticError(f"Index for '{name}' must be integer")
        return info['type']

    def analyze_for_loop(self, node):
        _, counter, bound_expr, step_expr, body = node

        if self.lookup(counter)['type'] != 'int':
            raise SemanticError("Loop counter must be integer")

        if self.analyze(bound_expr) != 'int':
            raise SemanticError("Loop boundary must be integer")

        if self.analyze(step_expr) != 'int':
            raise SemanticError("Loop step must be integer")

        for stmt in body:
            self.analyze(stmt)

    def analyze_switch(self, node):
        _, cond, choice, block, elseblock = node
        if self.analyze(cond) != 'bool':
            raise SemanticError("Switch condition must be boolean")
        for stmt in block:
            self.analyze(stmt)
        if elseblock:
            for stmt in elseblock[1]:
                self.analyze(stmt)

    def analyze_move(self, node):
        return None

    def analyze_rotate_left(self, node):
        return None

    def analyze_rotate_right(self, node):
        return None

    def analyze_get_environment(self, node):
        return 'bool'

    def analyze_result(self, node):
        return self.analyze(node[1])

    def _node_contains_result(self, node) -> bool:
        if isinstance(node, tuple):
            if node and node[0] == 'result':
                return True
            return any(self._node_contains_result(child) for child in node[1:])
        if isinstance(node, list):
            return any(self._node_contains_result(child) for child in node)
        return False

    def analyze_task_function(self, node):
        _, fname, params, body = node

        if len(self.scopes) != 1:
            raise SemanticError("TASK can only be declared at global scope")

        if fname in self.functions:
            if self.functions[fname]['params'] != params:
                raise SemanticError(f"Parameter list mismatch in '{fname}'")
        else:
            self.functions[fname] = { 'params': params, 'defined': False }

        prev_in = self.in_function
        self.in_function = True
        self.enter_scope()
        for p in params:
            self.declare(p, { 'type': 'unknown', 'dimensions': [] })

        if not self._node_contains_result(body):
            raise SemanticError("Missing RESULT in function")

        self.leave_scope()
        self.in_function = prev_in

    def analyze_function_call(self, node):
        _, fname, args = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")
        sig = self.functions[fname]['params']
        if len(args) != len(sig):
            raise SemanticError(f"Argument count mismatch in call '{fname}'")
        for a in args:
            self.analyze(a)

    def analyze_get_function_result(self, node):
        _, fname = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")
        return 'int'

    def analyze_uminus(self, node):
        if self.analyze(node[1]) != 'int':
            raise SemanticError("Unary minus only for integers")
        return 'int'

    def analyze_elementwise_comparison_two(self, node):
        _, op, left, right = node
        if self.analyze(left) != 'int' or self.analyze(right) != 'int':
            raise SemanticError(f"{op} expects integer operands")
        return 'bool'      # result is an array of bools
