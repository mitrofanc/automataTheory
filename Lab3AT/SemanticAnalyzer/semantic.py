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

        # --- 3) список узлов — двухфазный проход ---
        if isinstance(node, list):
            # Фаза 1: forward-declare всех TASK-функций
            for n in node:
                if isinstance(n, tuple) and n[0] == 'task_function':
                    _, fname, params, _ = n
                    if fname not in self.functions:
                        # ещё не было даже forward-decl
                        self.functions[fname] = { 'params': params, 'defined': False }
            # Фаза 2: рекурсивный детальный анализ
            for n in node:
                self.analyze(n)
            return

        # --- 4) кортеж-узел AST: dispatch по тегу ---
        nodetype = node[0]
        method = getattr(self, f'analyze_{nodetype}', self.generic_analyze)
        return method(node)

    def generic_analyze(self, node):
        """Ветка по умолчанию — если для узла нет analyze_<nodetype>."""
        raise SemanticError(f"No semantic rule for node type {node[0]}")

    # --------------------------------------------------------------------
    # Вспомогательные утилиты
    # --------------------------------------------------------------------
    def literal_type(self, node):
        """
        Определить тип литерала: ('literal', value).
        bool → 'bool', иначе → 'int'
        """
        v = node[1]
        return 'bool' if isinstance(v, bool) else 'int'

    def check_dimensions(self, name: str, dims: list):
        """
        Проверить, что все измерения dims (список узлов expression)
        — положительные целые.
        """
        for d in dims:
            if self.analyze(d) != 'int':
                raise SemanticError(f"Dimension in '{name}' must be integer")
            if isinstance(d, tuple) and d[0] == 'literal' and isinstance(d[1], int) and d[1] <= 0:
                raise SemanticError(f"Dimension in '{name}' must be positive")

    # --------------------------------------------------------------------
    # var_declaration : VAR IDENTIFIER dimensions_opt ASSIGN expression
    # --------------------------------------------------------------------
    def analyze_var_declaration(self, node):
        """
        Объявление переменной (массив или скаляр):
        node == ('var_declaration', name, dims_list, expr_node)
        """
        _, name, dims, expr = node

        # Специально для GET ENVIRONMENT: без явных скобок
        # даём ему форму 3×3×2
        if isinstance(expr, tuple) and expr[0] == 'get_environment':
            # если пользователь не задал размерности — подставляем [3,3,2]
            if not dims:
                # представляем их как литералы
                dims = [
                    ('literal', 3),
                    ('literal', 3),
                    ('literal', 2)
                ]

        # 1) проверяем корректность всех dims
        self.check_dimensions(name, dims)
        # 2) анализ правой части, узнать expr_type
        expr_type = self.analyze(expr)
        # 3) регистрируем новую переменную с её типом и формой
        self.declare(name, {
            'type': expr_type,
            'dimensions': dims
        })
        return expr_type

    # --------------------------------------------------------------------
    # assignment : IDENTIFIER ASSIGN expression
    # --------------------------------------------------------------------
    def analyze_assignment(self, node):
        """
        Присваивание:
        node == ('assignment', name, expr_node)
        """
        _, name, expr = node
        var = self.lookup(name)
        expr_type = self.analyze(expr)

        # если тип ещё 'unknown' (параметр функции), инициализируем
        if var.get('type') == 'unknown':
            var['type'] = expr_type
            return expr_type

        # иначе проверяем совпадение типов
        if var['type'] != expr_type:
            raise SemanticError(f"Type mismatch on assignment to '{name}'")
        return expr_type

    # --------------------------------------------------------------------
    # binop, logical AND/NOT, MXTRUE, MXFALSE
    # --------------------------------------------------------------------
    def analyze_binop(self, node):
        _, op, left, right = node
        lt = self.analyze(left)
        rt = self.analyze(right)

        # параметры функции могут оставаться с типом 'unknown'
        # трактуем их как целые — это устраняет ложный конфликт типов
        if lt == 'unknown':
            lt = 'int'
        if rt == 'unknown':
            rt = 'int'

        # арифметические
        if op in ['+', '-', '*', '/']:
            if (lt, rt) != ('int', 'int'):
                raise SemanticError(f"Operator '{op}' needs integer operands")
            return 'int'

        # логическое И
        if op == 'AND':
            if (lt, rt) != ('bool', 'bool'):
                raise SemanticError("Operator AND needs boolean operands")
            return 'bool'

        return None

    def analyze_not(self, node):
        """
        ('not', expr_node)
        """
        if self.analyze(node[1]) != 'bool':
            raise SemanticError("NOT requires boolean operand")
        return 'bool'

    def analyze_and(self, node):
        """('and', left, right) — same as binop AND."""
        return self.analyze_binop(node)

    def analyze_mxtrue(self, node):
        """('mxtrue', expr) ≡ NOT(expr)."""
        return self.analyze_not(node)

    def analyze_mxfalse(self, node):
        """('mxfalse', expr) ≡ NOT(expr)."""
        return self.analyze_not(node)

    # --------------------------------------------------------------------
    # comparison_zero и elementwise_comparison_zero
    # --------------------------------------------------------------------
    def analyze_comparison_zero(self, node):
        """
        ('comparison_zero', op, expr)
        ex: expr MXEQ → bool
        """
        _, op, expr = node
        if self.analyze(expr) != 'int':
            raise SemanticError(f"{op} requires integer operand")
        return 'bool'

    def analyze_elementwise_comparison_zero(self, node):
        """
        ('elementwise_comparison_zero', op, expr)
        ex: ELEQ expr → [bool]
        но мы заботимся только о типе результата — bool
        """
        _, op, expr = node
        if self.analyze(expr) != 'int':
            raise SemanticError(f"{op} requires integer operand")
        return 'bool'

    # --------------------------------------------------------------------
    # literal, expr-wrapper и array_literal
    # --------------------------------------------------------------------
    def analyze_literal(self, node):
        """
        ('literal', value)
        """
        return self.literal_type(node)

    def analyze_expr(self, node):
        """
        ('expr', inner_node)
        просто распаковать
        """
        return self.analyze(node[1])

    def analyze_array_literal(self, node):
        """
        ('array_literal', [expr1, expr2, …])
        Проверяем, что все выражения дают один тип.
        """
        _, elems = node
        if not elems:
            return 'int'   # пустой массив → по умолчанию int
        base = self.analyze(elems[0])
        for e in elems[1:]:
            if self.analyze(e) != base:
                raise SemanticError("Array elements must have the same type")
        return base

    # --------------------------------------------------------------------
    # SIZE, LOGITIZE/DIGITIZE, REDUCE/EXTEND
    # --------------------------------------------------------------------
    def analyze_size_operator(self, node):
        """
        ('size_operator', name)  — SIZE(name)
        """
        _, name = node
        self.lookup(name)
        return 'int'

    def analyze_type_conversion(self, node):
        """
        ('type_conversion', op, name) — LOGITIZE/DIGITIZE name
        всегда int
        """
        _, op, name = node
        self.lookup(name)
        return 'int'

    def analyze_size_change(self, node):
        """
        ('size_change', op, name, dims) — REDUCE/EXTEND
        """
        _, op, name, dims = node
        self.lookup(name)
        self.check_dimensions(name, dims)
        return 'int'

    # --------------------------------------------------------------------
    # array_access : IDENTIFIER [indices]
    # --------------------------------------------------------------------
    def analyze_array_access(self, node):
        """
        ('array_access', name, [idx1, idx2, …])
        """
        _, name, idx = node
        info = self.lookup(name)
        if len(idx) != len(info['dimensions']):
            raise SemanticError(f"Index count mismatch for '{name}'")
        for d in idx:
            if self.analyze(d) != 'int':
                raise SemanticError(f"Index for '{name}' must be integer")
        return info['type']

    # FOR counter BOUNDARY expr STEP expr block
    def analyze_for_loop(self, node):
        _, counter, bound_expr, step_expr, body = node

        # счётчик цикла должен быть объявлен как int
        if self.lookup(counter)['type'] != 'int':
            raise SemanticError("Loop counter must be integer")

        # граница – любое выражение, проверяем что она int
        if self.analyze(bound_expr) != 'int':
            raise SemanticError("Loop boundary must be integer")

        # шаг теперь произвольное выражение; главное, чтобы это был int
        if self.analyze(step_expr) != 'int':
            raise SemanticError("Loop step must be integer")

        # анализируем тело цикла
        for stmt in body:
            self.analyze(stmt)

    def analyze_switch(self, node):
        """
        ('switch', cond_expr, choice_bool, block, else_opt)
        """
        _, cond, choice, block, elseblock = node
        if self.analyze(cond) != 'bool':
            raise SemanticError("Switch condition must be boolean")
        for stmt in block:
            self.analyze(stmt)
        if elseblock:
            # elseblock == (choice_alt, block_list)
            for stmt in elseblock[1]:
                self.analyze(stmt)

    # --------------------------------------------------------------------
    # Команды робота: MOVE, ROTATE, GET ENVIRONMENT
    # --------------------------------------------------------------------
    def analyze_move(self, node):
        return None

    def analyze_rotate_left(self, node):
        return None

    def analyze_rotate_right(self, node):
        return None

    def analyze_get_environment(self, node):
        # GET ENVIRONMENT → bool
        return 'bool'

    # --------------------------------------------------------------------
    # RESULT внутри функции
    # --------------------------------------------------------------------
    def analyze_result(self, node):
        """
        ('result', expr_node)
        """
        return self.analyze(node[1])

    # --------------------------------------------------------------------
    # TASK-функция: task_function и связанный анализ
    # --------------------------------------------------------------------
    def analyze_task_function(self, node):
        """
        ('task_function', name, params_list, body_list)
        Обработка декларации и тела TASK.
        """
        _, fname, params, body = node

        # TASK можно только в глобальной области
        if len(self.scopes) != 1:
            raise SemanticError("TASK can only be declared at global scope")

        # forward-declared на этапе analyze(list):
        if fname in self.functions:
            # сверить сигнатуру
            if self.functions[fname]['params'] != params:
                raise SemanticError(f"Parameter list mismatch in '{fname}'")
        else:
            self.functions[fname] = { 'params': params, 'defined': False }

        # анализ тела функции
        prev_in = self.in_function
        self.in_function = True
        self.enter_scope()
        # объявить параметры как переменные с type='unknown'
        for p in params:
            self.declare(p, { 'type': 'unknown', 'dimensions': [] })

        seen_result = False
        for stmt in body:
            if isinstance(stmt, tuple) and stmt[0] == 'result':
                seen_result = True
            self.analyze(stmt)
        if not seen_result:
            raise SemanticError("Missing RESULT in function")

        self.leave_scope()
        self.in_function = prev_in

    # --------------------------------------------------------------------
    # DO function_call и GET get_function_result
    # --------------------------------------------------------------------
    def analyze_function_call(self, node):
        """
        ('function_call', name, args_list)
        """
        _, fname, args = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")
        sig = self.functions[fname]['params']
        if len(args) != len(sig):
            raise SemanticError(f"Argument count mismatch in call '{fname}'")
        for a in args:
            self.analyze(a)

    def analyze_get_function_result(self, node):
        """
        ('get_function_result', name)
        """
        _, fname = node
        if fname not in self.functions:
            raise SemanticError(f"Function '{fname}' not declared")
        # возвращаем всегда int
        return 'int'

    def analyze_uminus(self, node):
        # node = ('uminus', operand)
        if self.analyze(node[1]) != 'int':
            raise SemanticError("Unary minus only for integers")
        return 'int'

