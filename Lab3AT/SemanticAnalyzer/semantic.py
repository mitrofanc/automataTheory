from collections import namedtuple

class Type(namedtuple("Type", ["base", "dims"])):
    __slots__ = ()

    @property
    def is_array(self):
        return len(self.dims) > 0

    def __str__(self):
        if self.is_array:
            return f"{self.base}[{', '.join(map(str, self.dims))}]"
        return self.base

INT = Type('int', ())
BOOL = Type('bool', ())

def array_of(base_type: Type, dims):
    return Type(base_type.base, tuple(dims))

class SemanticAnalyzer:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.errors = []

    def analyze(self, ast):
        self._dispatch(ast)

    def _dispatch(self, node):
        node_type = node[0]
        method = getattr(self, f"_ana_{node_type}", None)
        if not method:
            raise SemanticError(f"Неизвестный тип AST-узла: {node_type}")
        return method(*node[1:])

    def _ana_program(self, statements):
        for st in statements:
            self._dispatch(st)

    def _ana_group(self, statements):
        for st in statements:
            self._dispatch(st)

    def _ana_var_decl(self, name, dims_ast, expr_ast):
        if name in self.vars:
            raise SemanticError(f"Повторное объявление переменной «{name}»")

        dims = []
        for d in dims_ast:
            t = self._dispatch(d)
            if t.base != 'int' or t.is_array:
                raise SemanticError("Размерность массива должна быть скаляром int")
            dims.append(-1)

        value_type = self._dispatch(expr_ast)

        if dims and not value_type.is_array:
            raise SemanticError("Нельзя инициализировать массив скалярным значением")

        declared_type = array_of(value_type, dims) if dims else value_type
        self.vars[name] = declared_type
        return declared_type

    def _ana_assign(self, name, expr_ast):
        if name not in self.vars:
            raise SemanticError(f"Необъявленная переменная «{name}»")
        lhs_type = self.vars[name]
        rhs_type = self._dispatch(expr_ast)
        if lhs_type.base != rhs_type.base or lhs_type.is_array != rhs_type.is_array:
            raise SemanticError(f"Несовместимые типы при присваивании {lhs_type} ← {rhs_type}")
        return lhs_type

    def _ana_move(self):
        return BOOL

    def _ana_rotate(self, direction):
        if direction not in ('LEFT', 'RIGHT'):
            raise SemanticError("ROTATE допускает только LEFT или RIGHT")
        return BOOL

    def _ana_for(self, counter, boundary_ast, step_ast, body):
        if counter not in self.vars or self.vars[counter].base != 'int':
            raise SemanticError(f"Cчётчик цикла «{counter}» должен быть объявленным int")
        b_type = self._dispatch(boundary_ast)
        s_type = self._dispatch(step_ast)
        if b_type.base != 'int' or s_type.base != 'int':
            raise SemanticError("BOUNDARY и STEP цикла должны быть int")
        for st in body:
            self._dispatch(st)

    def _ana_switch(self, cond_ast, true_body, false_body):
        cond_type = self._dispatch(cond_ast)
        if cond_type.base != 'bool':
            raise SemanticError("Условие в SWITCH должно быть bool")
        for st in true_body:
            self._dispatch(st)
        if false_body:
            for st in false_body:
                self._dispatch(st)

    def _ana_task(self, name, params, body):
        if name in self.funcs:
            raise SemanticError(f"Функция «{name}» уже объявлена")
        self.funcs[name] = (params, body)
        prev_vars = self.vars.copy()
        for p in params:
            self.vars[p] = INT
        for st in body:
            self._dispatch(st)
        self.vars = prev_vars

    def _ana_do(self, name, args):
        if name not in self.funcs:
            raise SemanticError(f"Вызов несуществующей функции «{name}»")
        params, _ = self.funcs[name]
        if len(params) != len(args):
            raise SemanticError(f"Аргументов ({len(args)}) не совпадает с параметрами ({len(params)})")
        for arg in args:
            self._dispatch(arg)
        return INT

    def _ana_get(self, name):
        if name not in self.funcs:
            raise SemanticError(f"GET неизвестной функции «{name}»")
        return INT

    def _ana_result(self, name):
        if name not in self.vars:
            raise SemanticError(f"Необъявленная переменная в RESULT: {name}")

    def _ana_binop(self, op, left_ast, right_ast):
        lt = self._dispatch(left_ast)
        rt = self._dispatch(right_ast)
        if op in ('+', '-', '*', '/'):
            self._assert_scalar_int(lt)
            self._assert_scalar_int(rt)
            return INT
        if op == 'AND':
            self._assert_scalar_bool(lt)
            self._assert_scalar_bool(rt)
            return BOOL
        raise SemanticError(f"Неизвестный бинарный оператор {op}")

    def _ana_not(self, expr_ast):
        t = self._dispatch(expr_ast)
        self._assert_scalar_bool(t)
        return BOOL

    def _ana_mxtrue(self, expr_ast):
        t = self._dispatch(expr_ast)
        self._assert_array_bool(t)
        return BOOL

    def _ana_mxfalse(self, expr_ast):
        t = self._dispatch(expr_ast)
        self._assert_array_bool(t)
        return BOOL

    def _ana_mxcomp(self, op, expr_ast):
        t = self._dispatch(expr_ast)
        self._assert_array_int(t)
        return BOOL

    def _ana_elecomp(self, op, expr_ast):
        t = self._dispatch(expr_ast)
        self._assert_array_int(t)
        return t

    def _ana_cast(self, op, ident):
        if ident not in self.vars:
            raise SemanticError(f"Преобразование неизвестной переменной «{ident}»")
        t = self.vars[ident]
        if op == 'LOGITIZE':
            return array_of(BOOL, t.dims)
        if op == 'DIGITIZE':
            return array_of(INT, t.dims)
        raise SemanticError("Неизвестный оператор преобразования")

    def _ana_resize(self, op, ident, dims_ast):
        if ident not in self.vars:
            raise SemanticError(f"REDUCE/EXTEND неизвестной переменной «{ident}»")
        base_t = self.vars[ident]
        dims = tuple(-1 for _ in dims_ast) if dims_ast else base_t.dims
        return array_of(base_t, dims)

    def _ana_size(self, ident):
        if ident not in self.vars:
            raise SemanticError(f"SIZE неизвестной переменной «{ident}»")
        return INT

    def _ana_get_environment(self):
        return array_of(BOOL, (-1, -1, -1))

    def _ana_int(self, value):
        return INT

    def _ana_bool(self, value):
        return BOOL

    def _ana_var(self, name):
        if name not in self.vars:
            raise SemanticError(f"Использование необъявленной переменной «{name}»")
        return self.vars[name]

    def _assert_scalar_int(self, t):
        if not (t.base == 'int' and not t.is_array):
            raise SemanticError("Ожидался скаляр int")

    def _assert_scalar_bool(self, t):
        if not (t.base == 'bool' and not t.is_array):
            raise SemanticError("Ожидался скаляр bool")

    def _assert_array_int(self, t):
        if not (t.base == 'int' and t.is_array):
            raise SemanticError("Ожидался массив int")

    def _assert_array_bool(self, t):
        if not (t.base == 'bool' and t.is_array):
            raise SemanticError("Ожидался массив bool")

class SemanticError(Exception):
    pass
