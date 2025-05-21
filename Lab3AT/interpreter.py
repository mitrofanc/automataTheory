from SemanticAnalyzer.semantic import SemanticAnalyzer, SemanticError
from Parser.parser import parser

class RuntimeErrorRobot(Exception):
    pass

class Interpreter:
    def __init__(self, source_code, robot_state, maze):
        self.ast = parser.parse(source_code)
        SemanticAnalyzer().analyze(self.ast)
        self.robot = robot_state
        self.maze = maze
        self.vars = {}
        self.funcs = {}
        self.findexit_path = None
        self.in_findexit = False

        self.commands = []
        self._flatten_ast(self.ast)
        self.step_index = 0

    def _flatten_ast(self, node):
        if node is None:
            return
        tag = node[0]

        if tag == 'program':
            for stmt in node[1]:
                self._flatten_ast(stmt)
        elif tag == 'group':
            for stmt in node[1]:
                self._flatten_ast(stmt)
        elif tag == 'move':
            self.commands.append(('move',))
        elif tag == 'rotate':
            self.commands.append(('rotate', node[1]))
        elif tag == 'for':
            counter, boundary, step, body = node[1], node[2], node[3], node[4]
            b = self._eval(boundary) if isinstance(boundary, tuple) else boundary
            st = self._eval(step) if isinstance(step, tuple) else step
            i = self.vars.get(counter, 0)
            if st == 0:
                return
            for v in range(i, b, st):
                self.vars[counter] = v
                for s in body:
                    self._flatten_ast(s)
        elif tag == 'task':
            name = node[1]
            params = node[2]
            body = node[3]
            self.funcs[name] = (params, body)
        elif tag == 'do':
            name = node[1]
            args = node[2]
            if name.upper() == 'FINDEXIT':
                self.findexit_path = self.maze.find_path()
                self.in_findexit = True
            if name not in self.funcs:
                raise RuntimeErrorRobot(f'Нет функции {name}')
            params, body = self.funcs[name]
            if len(params) != len(args):
                raise RuntimeErrorRobot('Число аргументов ≠ числу параметров')
            backup_vars = self.vars.copy()
            for p, a in zip(params, args):
                self.vars[p] = self._eval(a)
            for s in body:
                self._flatten_ast(s)
            self.vars = backup_vars
        elif tag == 'assign':
            self.commands.append(('assign', node[1], node[2]))
        elif tag == 'result':
            self.commands.append(('result', node[1]))

    def _eval(self, expr):
        tag = expr[0]
        if tag == 'int':
            return expr[1]
        if tag == 'var':
            return self.vars.get(expr[1], 0)
        return 0

    def step(self):
        if self.step_index >= len(self.commands):
            return False
        cmd = self.commands[self.step_index]
        if cmd[0] == 'move':
            if not self.robot.move():
                raise RuntimeErrorRobot("MOVE failed — стена")
            self.robot.check_panic()
        elif cmd[0] == 'rotate':
            dir = cmd[1].lower()
            if dir == 'left':
                self.robot.rotate_left()
            else:
                self.robot.rotate_right()
        elif cmd[0] == 'assign':
            name = cmd[1]
            val_expr = cmd[2]
            val = self._eval(val_expr)
            self.vars[name] = val
        elif cmd[0] == 'result':
            pass
        self.step_index += 1
        return True

    def run(self):
        while self.step():
            pass
