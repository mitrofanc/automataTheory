from SemanticAnalyzer.semantic import SemanticAnalyzer
from Parser.parser import parser
class Interpreter:
    def __init__(self, source_code, robot_state, maze, after_step = None):
        self.ast = parser.parse(source_code)
        SemanticAnalyzer().analyze(self.ast)
        self.robot = robot_state
        self.maze = maze
        self.after_step = after_step

        self.vars: dict[str, list] = {}
        self.funcs: dict[str, tuple[list[str], list]] = {}
        self.current_func = None

    def _as_array(self, v):
        return v if isinstance(v, list) else [v]

    def _binary_elementwise(self, left, right, op):
        a, b = self._flatten(left), self._flatten(right)
        if len(a) == 1:
            a *= len(b)
        if len(b) == 1:
            b *= len(a)
        if len(a) != len(b):
            raise RuntimeErrorRobot("Inconsistent array dimensions")
        res = [op(x, y) for x, y in zip(a, b)]
        return res[0] if len(res) == 1 else res

    def _majority(self, arr, predicate):
        data = self._flatten(arr)
        cnt_true = sum(1 for x in data if predicate(x))
        return cnt_true > len(data) // 2

    def _infer_shape(self, value):
        if not isinstance(value, list):
            return [1]

        if not value:
            return [0]

        first = self._infer_shape(value[0])
        for elem in value:
            if self._infer_shape(elem) != first:
                raise RuntimeErrorRobot("Inconsistent shape")
        return [len(value)] + first

    def _tick(self):
        if self.after_step:
            self.after_step(self.robot)

    def _flatten(self, v):
        if not isinstance(v, list):
            return [v]
        out = []
        for e in v:
            out.extend(self._flatten(e))
        return out

    def _eval(self, expr):
        if isinstance(expr, (int, bool, list)):
            return expr

        if isinstance(expr, str):
            if expr not in self.vars:
                raise RuntimeErrorRobot(f"Undeclared variable {expr}")
            return self.vars[expr]

        if isinstance(expr, tuple) and expr[0] == 'get_environment':
            env = self.robot.get_environment()
            self.vars['lastEnv'] = env
            return env

        if not isinstance(expr, tuple):
            raise RuntimeErrorRobot(f"Unknown type of expression: {expr}")

        tag = expr[0]

        if tag == 'get_function_result':
            func_name = expr[1]
            return self.vars.get(f"res_{func_name}")

        if tag == 'uminus':
            val = self._eval(expr[1])
            arr = self._as_array(val)
            res = [-x for x in arr]
            return res[0] if not isinstance(val, list) else res

        if tag == 'expr':
            return self._eval(expr[1])

        if tag == 'literal':
            val = expr[1]
            if isinstance(val, str):
                return True if val.upper() == 'TRUE' else False
            return val

        if tag == 'array_literal':
            return [self._eval(e) if isinstance(e, tuple) else e for e in expr[1]]

        if tag == 'array_access':
            name, indices_raw = expr[1], expr[2]
            arr = self.vars.get(name)
            if arr is None:
                raise RuntimeErrorRobot(f"Undeclared variable {name}")
            indices = [self._eval(i) for i in indices_raw]
            # 1‑based индексация по ТЗ
            elem = arr
            for idx in indices:
                if not isinstance(elem, list):
                    raise RuntimeErrorRobot("Index to scalar")
                if idx < 1 or idx > len(elem):
                    raise RuntimeErrorRobot("Index over the array length")
                elem = elem[idx - 1]
            return elem
        if tag == 'size_operator':
            name = expr[1]
            arr = self.vars.get(name)
            if arr is None:
                raise RuntimeErrorRobot(f"Undeclared variable {name}")
            return len(self._as_array(arr))
        if tag == 'type_conversion':
            op, name = expr[1], expr[2]
            value = self.vars.get(name)
            if value is None:
                raise RuntimeErrorRobot(f"Undeclared variable {name}")
            if op == 'LOGITIZE':
                return [bool(x) for x in self._as_array(value)]
            else:
                return [int(bool(x)) for x in self._as_array(value)]

        if tag == 'binop':
            left = self._eval(expr[2])
            right = self._eval(expr[3])
            op_sym = expr[1]
            if op_sym == '+':
                return self._binary_elementwise(left, right, lambda a, b: a + b)
            if op_sym == '-':
                return self._binary_elementwise(left, right, lambda a, b: a - b)
            if op_sym == '*':
                return self._binary_elementwise(left, right, lambda a, b: a * b)
            if op_sym == '/':
                return self._binary_elementwise(left, right, lambda a, b: a // b if b != 0 else RuntimeErrorRobot("Division by 0"))

        if tag == 'and':
            l = self._eval(expr[1])
            r = self._eval(expr[2])
            return [bool(a) and bool(b) for a, b in zip(self._as_array(l), self._as_array(r))]

        if tag == 'not':
            val = self._eval(expr[1])
            return [not bool(x) for x in self._as_array(val)]

        if tag == 'comparison_zero':
            op_sym, operand = expr[1], self._eval(expr[2])
            data = self._as_array(operand)
            if op_sym == 'MXEQ':
                return self._majority(data, lambda x: x == 0)
            if op_sym == 'MXLT':
                return self._majority(data, lambda x: x < 0)
            if op_sym == 'MXGT':
                return self._majority(data, lambda x: x > 0)
            if op_sym == 'MXLTE':
                return self._majority(data, lambda x: x <= 0)
            if op_sym == 'MXGTE':
                return self._majority(data, lambda x: x >= 0)

        if tag == 'elementwise_comparison_zero':
            op_sym, operand_expr = expr[1], expr[2]
            operand_val = self._eval(operand_expr)
            data = self._flatten(operand_val)
            mapping = {
                'ELEQ': lambda x: x == 0,
                'ELLT': lambda x: x < 0,
                'ELGT': lambda x: x > 0,
                'ELLTE': lambda x: x <= 0,
                'ELGTE': lambda x: x >= 0,
            }
            return [mapping[op_sym](x) for x in data]

        if tag == 'elementwise_comparison_two':
            op_sym, left_expr, right_expr = expr[1], expr[2], expr[3]

            left_vals = self._flatten(self._eval(left_expr))
            right_vals = self._flatten(self._eval(right_expr))

            # broadcast
            if len(left_vals) == 1: left_vals *= len(right_vals)
            if len(right_vals) == 1: right_vals *= len(left_vals)
            if len(left_vals) != len(right_vals):
                raise RuntimeErrorRobot("Array length mismatch in elementwise comparison")

            cmp = {
                'ELEQ': lambda a, b: a == b,
                'ELLT': lambda a, b: a < b,
                'ELGT': lambda a, b: a > b,
                'ELLTE': lambda a, b: a <= b,
                'ELGTE': lambda a, b: a >= b,
            }[op_sym]
            return [cmp(a, b) for a, b in zip(left_vals, right_vals)]

        if tag == 'mxtrue':
            arr = self._eval(expr[1])
            return self._majority(arr, lambda x: bool(x))
        if tag == 'mxfalse':
            arr = self._eval(expr[1])
            return self._majority(arr, lambda x: not bool(x))

        if tag == 'expr' and isinstance(expr[1], str):
            name = expr[1]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Undeclared variable {name}")
            return self.vars[name]



        raise RuntimeErrorRobot(f"Undetected expression: {expr}")

    def _exec_block(self, stmts):
        for stmt in stmts:
            self._exec(stmt)

    def _exec(self, node):
        if node is None:
            return
        if not isinstance(node, tuple):
            raise RuntimeErrorRobot(f"Wrong node AST: {node}")

        tag = node[0]

        if tag == 'var_declaration':
            name, dims_raw, expr = node[1], node[2], node[3]

            raw_val = self._eval(expr)
            if dims_raw:
                value = raw_val if isinstance(raw_val, list) else [raw_val]
            else:
                value = raw_val
            declared_shape = None
            if dims_raw:
                declared_shape = [self._eval(d) for d in dims_raw]
                if any(not isinstance(d, int) or d <= 0 for d in declared_shape):
                    raise RuntimeErrorRobot("Dimensions need to positive")

            actual_shape = self._infer_shape(value)
            if declared_shape and len(actual_shape) > len(declared_shape):
                while len(actual_shape) > len(declared_shape) and actual_shape[-1] == 1:
                    actual_shape.pop()

            if declared_shape is not None:
                while len(declared_shape) > 1 and declared_shape[-1] == 1:
                    declared_shape.pop()
            if declared_shape is not None and declared_shape != actual_shape:
                raise RuntimeErrorRobot(f"Arrays`s size {actual_shape} not equals {declared_shape}")

            self.vars[name] = value
            return

        if tag == 'assignment':
            name, expr = node[1], node[2]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Undeclared variable {name}")
            self.vars[name] = self._eval(expr)
            return

        if tag == 'size_change':
            op, name, dims_raw = node[1], node[2], node[3]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Don`t have array {name}")
            arr = self._as_array(self.vars[name])
            if not dims_raw:
                raise RuntimeErrorRobot("REDUCE/EXTEND without size")
            new_size = self._eval(dims_raw[0])
            if op in ('REDUCE', 'reduce'):
                if new_size > len(arr):
                    raise RuntimeErrorRobot("REDUCE to bigger size")
                self.vars[name] = arr[:new_size]
            else:
                if new_size < len(arr):
                    raise RuntimeErrorRobot("EXTEND to smaller size")
                self.vars[name] = arr + [0] * (new_size - len(arr))
            return

        if tag == 'for_loop':
            counter, boundary_expr, step_expr, body = node[1], node[2], node[3], node[4]

            # bound to scalar
            raw_bound = self._eval(boundary_expr)
            bound_list = self._as_array(raw_bound)
            if len(bound_list) != 1:
                raise RuntimeErrorRobot("The loop boundary must be scalar")
            boundary = bound_list[0]

            # step to scalar
            raw_step = self._eval(step_expr)
            step_list = self._as_array(raw_step)
            if len(step_list) != 1:
                raise RuntimeErrorRobot("The step of the loop must be scalar")
            step_val = step_list[0]
            if step_val == 0:
                raise RuntimeErrorRobot("The cycle step is 0")

            self.vars[counter] = 1
            while self.vars[counter] < boundary:
                self._exec_block(body)
                self.vars[counter] += step_val
            return

        if tag == 'switch':
            cond_expr, true_literal, true_block, else_clause = node[1], node[2], node[3], node[4]
            cond_val = self._eval(cond_expr)
            if isinstance(cond_val, list) and len(cond_val) == 1:
                cond_val = cond_val[0]
            if isinstance(true_literal, bool):
                main_bool = true_literal
            else:
                main_bool = (true_literal.upper() == 'TRUE')
            chosen_block = true_block if cond_val == main_bool else (else_clause[1] if else_clause else [])
            self._exec_block(chosen_block)
            return

        if tag == 'move':
            if not self.robot.move():
                raise RuntimeErrorRobot("MOVE: wall ahead")
            self._tick()
            return
        if tag == 'rotate_left':
            self.robot.rotate_left()
            self._tick()
            return
        if tag == 'rotate_right':
            self.robot.rotate_right()
            self._tick()
            return

        if tag == 'task_function':
            name, params, body = node[1], node[2], node[3]
            self.funcs[name] = (params, body)
            return

        if tag == 'function_call':
            name, args = node[1], node[2]
            if name not in self.funcs:
                raise RuntimeErrorRobot(f"Don`t have func {name}")
            params, body = self.funcs[name]
            if len(params) != len(args):
                raise RuntimeErrorRobot("Number of arguments must match number of parameters")

            backup = self.vars.copy()
            for p, a in zip(params, args):
                self.vars[p] = self._eval(a)

            prev_func = self.current_func
            self.current_func = name
            self._exec_block(body)
            self.current_func = prev_func

            result_val = self.vars.get(f"res_{name}")
            self.vars = backup
            self.vars[f"res_{name}"] = result_val
            return result_val

        if tag == 'result':
            val = self._eval(node[1])
            if self.current_func is None:
                raise RuntimeErrorRobot("Result cannot be outside of function")
            print(f"Result {self.current_func}: {val}")
            self.vars[f"res_{self.current_func}"] = val
            return

        if tag == 'get_function_result':
            name = node[1]
            return self.vars.get(f"res_{name}")

        if tag in {'binop',
                   'and',
                   'not',
                   'mxtrue',
                   'mxfalse',
                   'comparison_zero',
                   'elementwise_comparison_zero',
                   'expr',
                   'literal',
                   'array_literal',
                   'size_operator',
                   'type_conversion',
                   'array_access'
                   }:
            self._eval(node)
            return

        raise RuntimeErrorRobot(f"Incorrect node tag {tag}")

    def run(self):
        try:
            for stmt in self.ast:
                tag = stmt[0]
                if tag not in ('var_declaration', 'task_function'):
                    raise RuntimeErrorRobot(f"«{tag}» operator is not allowed outside the function")
                self._exec(stmt)
            if 'FINDEXIT' in self.funcs:
                self._exec(('function_call', 'FINDEXIT', []))
        except RuntimeErrorRobot as e:
            print(f"Robot error: {e}")

class RuntimeErrorRobot(Exception):
    """Runtime Error Robot"""
