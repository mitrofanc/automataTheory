from SemanticAnalyzer.semantic import SemanticAnalyzer, SemanticError
from Parser.parser import parser            # импорт готового парсера

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
        self.findexit_path = None  # путь для FINDEXIT
        self.in_findexit = False

    # ───────── run ─────────
    def run(self):
        self._exec(self.ast)

    # ───────── dispatcher ─────────
    def _exec(self, node):
        tag = node[0]
        return getattr(self, f'_ex_{tag}')( *node[1:] )

    # ===== программные узлы =====
    def _ex_program(self, stmts):
        for s in stmts: self._exec(s)

    def _ex_group(self, stmts):
        for s in stmts: self._exec(s)

    # ---- VAR ----
    def _ex_var_decl(self, name, dims, expr):
        if name in self.vars:
            raise RuntimeErrorRobot(f'Повторное объявление {name}')
        self.vars[name] = self._eval(expr)

    # ---- ASSIGN ----
    def _ex_assign(self, name, expr):
        if name not in self.vars:
            raise RuntimeErrorRobot(f'Необъявленная {name}')
        self.vars[name] = self._eval(expr)

    # ---- MOVE / ROTATE ----
    def _ex_move(self):
        if not self.robot.move():
            raise RuntimeErrorRobot('MOVE failed — стена')
        self.robot.check_panic()

    def _ex_rotate(self, dir):
        getattr(self.robot, f'rotate_{dir.lower()}')()

    # ---- FOR ----
    def _ex_for(self, counter, boundary, step, body):
        if counter not in self.vars:
            raise RuntimeErrorRobot(f'Необъявлен счётчик {counter}')
        b = self._eval(boundary)
        st = self._eval(step)
        i = self.vars[counter]
        while (i < b and st>0) or (i > b and st<0):
            for s in body: self._exec(s)
            i += st
        self.vars[counter] = i

    # ---- SWITCH ----
    def _ex_switch(self, cond, t_body, f_body):
        if self._eval(cond):
            for s in t_body: self._exec(s)
        elif f_body:
            for s in f_body: self._exec(s)

    # ---- TASK / DO / GET ----
    def _ex_task(self, name, params, body):
        self.funcs[name] = (params, body)

    def _ex_do(self, name, args):
        if name not in self.funcs:
            raise RuntimeErrorRobot(f'Нет функции {name}')
        params, body = self.funcs[name]
        if len(params)!=len(args):
            raise RuntimeErrorRobot('Число аргументов ≠ числу параметров')
        backup = self.vars.copy()
        for p,a in zip(params,args):
            self.vars[p] = self._eval(a)
        for s in body: self._exec(s)
        self.vars = backup

    def _ex_get(self, name):
        # в этой версии просто игнор
        return None

    # ===== выражения =====
    def _eval(self, expr):
        tag = expr[0]
        return getattr(self, f'_ev_{tag}')( *expr[1:] )

    def _ev_int(self, v): return v
    def _ev_bool(self, v): return v
    def _ev_var(self, name):
        if name not in self.vars:
            raise RuntimeErrorRobot(f'Необъявленная {name}')
        return self.vars[name]

    def _ev_binop(self, op, l, r):
        a, b = self._eval(l), self._eval(r)
        if op=='+': return a+b
        if op=='-': return a-b
        if op=='*': return a*b
        if op=='/': return a//b
        if op=='AND': return a and b
        raise RuntimeErrorRobot(f'Неизвестный op {op}')

    def _ev_not(self, e): return not self._eval(e)

    # ---- SIZE ----
    def _ev_size(self, ident):
        v = self._ev_var(ident)
        return len(v) if isinstance(v, list) else 0

    # ---- LOGITIZE / DIGITIZE ----
    def _ev_cast(self, op, ident):
        v = self._ev_var(ident)
        if op=='LOGITIZE':
            return bool(v)
        return int(v)

    # ---- REDUCE / EXTEND ---- (на скаляры действует без изменений)
    def _ev_resize(self, op, ident, dims):
        v = self._ev_var(ident)
        if not isinstance(v, list):
            return v
        dim = self._eval(dims[0]) if dims else len(v)
        if op=='REDUCE':
            return v[:dim]
        else:  # EXTEND
            return v + [0]*(dim-len(v)) if isinstance(v[0],int) else v+[False]*(dim-len(v))

    # ---- GET ENVIRONMENT ----
    def _ev_get_environment(self):
        return self.robot.get_environment()

    # ---- MXTRUE / MXFALSE ----
    def _ev_mxtrue(self, expr):
        arr = self._eval(expr)
        flat = list(self._flatten(arr))
        return sum(bool(x) for x in flat) > len(flat)//2
    def _ev_mxfalse(self, expr):
        return not self._ev_mxtrue(expr)

    # ---- MXEQ / MXLT ... сравнение большинства ----
    def _ev_mxcomp(self, op, expr):
        arr = self._eval(expr); flat=list(self._flatten(arr))
        if op=='MXEQ':   return sum(x==0 for x in flat) > len(flat)//2
        if op=='MXLT':   return sum(x<0  for x in flat) > len(flat)//2
        if op=='MXGT':   return sum(x>0  for x in flat) > len(flat)//2
        if op=='MXLTE':  return sum(x<=0 for x in flat) > len(flat)//2
        if op=='MXGTE':  return sum(x>=0 for x in flat) > len(flat)//2

    # ---- ELEQ / ELLT ... поэлементно ----
    def _ev_elecomp(self, op, expr):
        arr = self._eval(expr)
        def comp(x):
            if op=='ELEQ':   return x==0
            if op=='ELLT':   return x<0
            if op=='ELGT':   return x>0
            if op=='ELLTE':  return x<=0
            if op=='ELGTE':  return x>=0
        return [comp(x) for x in arr]

    # util для свёртки
    def _flatten(self, v):
        if isinstance(v, list):
            for e in v:
                yield from self._flatten(e)
        else:
            yield v

    def _ex_task(self, name, params, body):
        self.funcs[name] = (params, body)

    def _ex_do(self, name, args):
        if name not in self.funcs:
            raise RuntimeErrorRobot(f'Нет функции {name}')
        params, body = self.funcs[name]
        if len(params) != len(args):
            raise RuntimeErrorRobot('Число аргументов ≠ числу параметров')
        backup = self.vars.copy()
        for p, a in zip(params, args):
            self.vars[p] = self._eval(a)

        # Особенность: если функция — FINDEXIT, считаем и сохраняем путь
        if name.upper() == "FINDEXIT":
            self.findexit_path = self.maze.find_path()
            self.in_findexit = True

        for s in body:
            self._exec(s)
        self.vars = backup

    # метод для возврата результата из FINDEXIT (можно расширить)
    def _ex_get(self, name):
        if name.upper() == "FINDEXIT" and self.findexit_path:
            return self.findexit_path
        return None