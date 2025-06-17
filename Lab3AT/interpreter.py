from SemanticAnalyzer.semantic import SemanticAnalyzer
from Parser.parser import parser

class RuntimeErrorRobot(Exception):
    """Ошибки времени выполнения языка клеточного робота."""


class Interpreter:
    """
    Полный однопроходный интерпретатор клеточного языка.
    Лексер/парсер создают AST (кортежи). Мы исполняем его рекурсивно,
    без предварительного «сплющивания» в список команд; это проще, чем
    поддерживать множество edge‑cases при разворачивании.
    """

    def __init__(self, source_code, robot_state, maze, after_step = None):
        # Построить AST и семантически проверить
        self.ast = parser.parse(source_code)
        SemanticAnalyzer().analyze(self.ast)

        # Объекты робота/лабиринта
        self.robot = robot_state
        self.maze = maze
        self.after_step = after_step

        # Переменные и функции (TASK)
        self.vars: dict[str, list] = {}
        self.funcs: dict[str, tuple[list[str], list]] = {}
        self.current_func = None  # активная task-функция

    # ------------------------------------------------------------------
    # Вспомогательные функции
    # ------------------------------------------------------------------
    def _as_array(self, v):
        """Любое значение превращаем в массив (скаляр → [скаляр])."""
        return v if isinstance(v, list) else [v]

    def _binary_elementwise(self, left, right, op):
        """Применяет бинарный op к двум массивам с простым броадкастом."""
        a, b = self._flatten(left), self._flatten(right)
        if len(a) == 1:
            a *= len(b)
        if len(b) == 1:
            b *= len(a)
        if len(a) != len(b):
            raise RuntimeErrorRobot("Несогласованные размерности массивов")
        return [op(x, y) for x, y in zip(a, b)]

    def _majority(self, arr, predicate):
        """Возвращает True, если большинство элементов удовлетворяют predicate."""
        data = self._flatten(arr)
        cnt_true = sum(1 for x in data if predicate(x))
        return cnt_true > len(data) // 2

    def _infer_shape(self, value):
        """
        Рекурсивно вычисляет форму массива.
        Скаляр → [1]; проверяет прямоугольность.
        """
        if not isinstance(value, list):
            return [1]

        if not value:  # пустой список
            return [0]

        first = self._infer_shape(value[0])
        for elem in value:
            if self._infer_shape(elem) != first:
                raise RuntimeErrorRobot("Нерегулярный (рваный) массив")
        return [len(value)] + first

    def _tick(self):
        """Вызывается после каждой физической команды робота."""
        if self.after_step:
            self.after_step(self.robot)  # передаём объект RobotState

    # ------------------------------------------------------------------
    #  Утилита: рекурсивно «выпрямляет» вложенный список в плоский
    #    [1,[2,3],[[4]],5] → [1,2,3,4,5]
    # ------------------------------------------------------------------
    def _flatten(self, v):
        if not isinstance(v, list):
            return [v]
        out = []
        for e in v:
            out.extend(self._flatten(e))
        return out

    # ------------------------------------------------------------------
    # Вычисление выражений
    # ------------------------------------------------------------------
    def _eval(self, expr):
        if isinstance(expr, (int, bool, list)):
            # Примитивы Python попадают сюда, если уже вычислены
            return expr

        # ——— Строка-идентификатор — возвращаем значение переменной ———
        if isinstance(expr, str):
            if expr not in self.vars:
                raise RuntimeErrorRobot(f"Необъявленная переменная {expr}")

            return self.vars[expr]

        if isinstance(expr, tuple) and expr[0] == 'get_environment':
            env = self.robot.get_environment()
            self.vars['lastEnv'] = env  # если нужно обращаться как lastEnv
            return env

        if not isinstance(expr, tuple):
            raise RuntimeErrorRobot(f"Неизвестный тип выражения: {expr}")

        tag = expr[0]

        if tag == 'get_function_result':
            func_name = expr[1]
            return self.vars.get(f"res_{func_name}")

        if tag == 'get_environment':
            env = self.robot.get_environment()
          # (опционально) сохраняем, если нужен доступ через lastEnv:
            self.vars['lastEnv'] = env
            return env
        # --- Унарный минус ---------------------------------------------
        if tag == 'uminus':
            val = self._eval(expr[1])
            arr = self._as_array(val)
            # сохраняем скалярность, если она была
            res = [-x for x in arr]
            return res[0] if not isinstance(val, list) else res

        # --- Литералы --------------------------------------------------
        if tag == 'expr':
            # Обёртка
            return self._eval(expr[1])

        if tag == 'literal':
            val = expr[1]
            if isinstance(val, str):
                # TRUE/FALSE приходят строкой из лексера
                return True if val.upper() == 'TRUE' else False
            return val  # уже int
        if tag == 'array_literal':
            return [self._eval(e) if isinstance(e, tuple) else e for e in expr[1]]
        if tag == 'array_access': # todo понять если надо
            name, indices_raw = expr[1], expr[2]
            arr = self.vars.get(name)
            if arr is None:
                raise RuntimeErrorRobot(f"Необъявленная переменная {name}")
            indices = [self._eval(i) for i in indices_raw]
            # 1‑based индексация по ТЗ
            elem = arr
            for idx in indices:
                if not isinstance(elem, list):
                    raise RuntimeErrorRobot("Индекс к скаляру")
                if idx < 1 or idx > len(elem):
                    raise RuntimeErrorRobot("Индекс за границей массива")
                elem = elem[idx - 1]
            return elem
        if tag == 'size_operator':
            name = expr[1]
            arr = self.vars.get(name)
            if arr is None:
                raise RuntimeErrorRobot(f"Необъявленная переменная {name}")
            return len(self._as_array(arr))
        if tag == 'type_conversion':
            op, name = expr[1], expr[2]
            value = self.vars.get(name)
            if value is None:
                raise RuntimeErrorRobot(f"Необъявленная переменная {name}")
            if op == 'LOGITIZE':
                return [bool(x) for x in self._as_array(value)]
            else:
                return [int(bool(x)) for x in self._as_array(value)]

        # --- Бинарная арифметика --------------------------------------
        if tag == 'binop': # здесь должны быть бинарные арифметические операции
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
                return self._binary_elementwise(left, right, lambda a, b: a // b if b != 0 else RuntimeErrorRobot("Деление на ноль"))

        # --- AND / NOT --------------------------------------------------
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

        # --- MXTRUE / MXFALSE ------------------------------------------
        if tag == 'mxtrue':
            arr = self._eval(expr[1])
            return self._majority(arr, lambda x: bool(x))
        if tag == 'mxfalse':
            arr = self._eval(expr[1])
            return self._majority(arr, lambda x: not bool(x))

        # --- идентификатор ---------------------------------------------
        if tag == 'expr' and isinstance(expr[1], str):
            name = expr[1]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Необъявленная переменная {name}")
            return self.vars[name]



        raise RuntimeErrorRobot(f"Неизвестное выражение: {expr}")

    # ------------------------------------------------------------------
    # Исполнение операторов (statements)
    # ------------------------------------------------------------------

    def _exec_block(self, stmts):
        for stmt in stmts:
            self._exec(stmt)

    def _exec(self, node):
        if node is None:
            return
        if not isinstance(node, tuple):
            raise RuntimeErrorRobot(f"Неверный узел AST: {node}")

        tag = node[0]

        if tag == 'var_declaration':
            name, dims_raw, expr = node[1], node[2], node[3]

            raw_val = self._eval(expr)
            value = raw_val if isinstance(raw_val, list) else [raw_val]

            # 1) объявленная форма (None, если скобок нет)
            declared_shape = None
            if dims_raw:
                declared_shape = [self._eval(d) for d in dims_raw]
                if any(not isinstance(d, int) or d <= 0 for d in declared_shape):
                    raise RuntimeErrorRobot("Размерности должны быть положительными целыми")

            # 2) фактическая форма
            actual_shape = self._infer_shape(value)
            # здесь надо вставить обрезание хвоста
            if declared_shape and len(actual_shape) > len(declared_shape):
                # убираем trailing 1
                while len(actual_shape) > len(declared_shape) and actual_shape[-1] == 1:
                    actual_shape.pop()

            # 3) обрезаем все завершающие 1 в declared_shape (скаляр [1] останется [1])
            if declared_shape is not None:
                while len(declared_shape) > 1 and declared_shape[-1] == 1:
                    declared_shape.pop()
            # 4) сверяем получившиеся формы
            if declared_shape is not None and declared_shape != actual_shape:
                raise RuntimeErrorRobot(f"Размер массива {actual_shape} не совпадает с объявленным {declared_shape}")

            # 4) сохраняем
            self.vars[name] = value
            return

            # ------------------ ПРИСВАИВАНИЕ -------------------------------
        if tag == 'assignment':
            name, expr = node[1], node[2]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Присваивание необъявленной переменной {name}")
            self.vars[name] = self._eval(expr)
            return

        # ---------------- size_change ----------------------------------
        if tag == 'size_change':
            op, name, dims_raw = node[1], node[2], node[3]
            if name not in self.vars:
                raise RuntimeErrorRobot(f"Массив {name} не объявлен")
            arr = self._as_array(self.vars[name])
            if not dims_raw:
                raise RuntimeErrorRobot("REDUCE/EXTEND без указания размера")
            new_size = self._eval(dims_raw[0])  # одномерно
            if op in ('REDUCE', 'reduce'):
                if new_size > len(arr):
                    raise RuntimeErrorRobot("REDUCE до большего размера")
                self.vars[name] = arr[:new_size]
            else:  # EXTEND
                if new_size < len(arr):
                    raise RuntimeErrorRobot("EXTEND до меньшего размера")
                self.vars[name] = arr + [0] * (new_size - len(arr))
            return

        # ---------------- for_loop -------------------------------------
        if tag == 'for_loop':
            # распаковываем всё сразу, step теперь — произвольное выражение
            counter, boundary_expr, step_expr, body = node[1], node[2], node[3], node[4]

            # 1) вычисляем и распаковываем границу в скаляр
            raw_bound = self._eval(boundary_expr)
            bound_list = self._as_array(raw_bound)
            if len(bound_list) != 1:
                raise RuntimeErrorRobot("Граница цикла должна быть скалярной")
            boundary = bound_list[0]

            # 2) вычисляем и распаковываем шаг в скаляр
            raw_step = self._eval(step_expr)
            step_list = self._as_array(raw_step)
            if len(step_list) != 1:
                raise RuntimeErrorRobot("Шаг цикла должен быть скалярным")
            step_val = step_list[0]
            if step_val == 0:
                raise RuntimeErrorRobot("Шаг цикла равен 0")

            # 3) запускаем цикл (1-based по ТЗ)
            self.vars[counter] = 1
            while self.vars[counter] < boundary:
                self._exec_block(body)
                self.vars[counter] += step_val
            return

        # ---------------- switch ---------------------------------------
        if tag == 'switch':
            cond_expr, true_literal, true_block, else_clause = node[1], node[2], node[3], node[4]
            cond_val = self._eval(cond_expr)
            # true_literal может быть либо строкой 'TRUE'/'FALSE', либо уже Python-булем True/False.
            if isinstance(true_literal, bool):
                main_bool = true_literal
            else:
                main_bool = (true_literal.upper() == 'TRUE')
            chosen_block = true_block if cond_val == main_bool else (else_clause[1] if else_clause else [])
            self._exec_block(chosen_block)
            return

        # ---------------- robot commands --------------------------------
        if tag == 'move':
            if not self.robot.move():
                raise RuntimeErrorRobot("MOVE: впереди стена")
            self.robot.check_panic()
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
        # if tag == 'get_environment':
        #     env = self.robot.get_environment()  # 3×3×3 список True/False
        #     return env

        # ---------------- функции TASK/DO/GET ---------------------------
        if tag == 'task_function':
            name, params, body = node[1], node[2], node[3]
            self.funcs[name] = (params, body)
            return
        if tag == 'function_call':
            name, args = node[1], node[2]
            if name not in self.funcs:
                raise RuntimeErrorRobot(f"Нет функции {name}")
            params, body = self.funcs[name]
            if len(params) != len(args):
                raise RuntimeErrorRobot("Число аргументов не совпадает")

            # --- формируем новую «локальную» область ---------------
            backup = self.vars.copy()  # сохраним глобалы
            for p, a in zip(params, args):  # простая передача по ссылке «через объект»
                self.vars[p] = self._eval(a)

            prev_func = self.current_func
            self.current_func = name  # нужно для result
            self._exec_block(body)
            self.current_func = prev_func

            result_val = self.vars.get(f"res_{name}")
            self.vars = backup  # локальные переменные исчезают
            self.vars[f"res_{name}"] = result_val
            return result_val

        if tag == 'result':
            val = self._eval(node[1])
            if self.current_func is None:
                raise RuntimeErrorRobot("Оператор result вне тела функции")
            # сохраняем под именем res_<func>
            self.vars[f"res_{self.current_func}"] = val
            return  # после result продолжать можно, ТЗ не запрещает

        if tag == 'get_function_result':
            name = node[1]
            # Для простоты результат функции хранится в vars[f"res_{name}"]
            return self.vars.get(f"res_{name}")

        # ---------------- выражение как statement -----------------------
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
            # side‑effect‑free, просто вычисляем и игнорируем
            self._eval(node)
            return

        raise RuntimeErrorRobot(f"Неизвестный тег узла {tag}")

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------
    def run(self):
        try:
            for stmt in self.ast:
                tag = stmt[0]
                # разрешены лишь объявления: var и task
                if tag not in ('var_declaration', 'task_function'):
                    raise RuntimeErrorRobot(f"Оператор «{tag}» вне функции не разрешён")
                self._exec(stmt)
            # автоматический запуск FINDEXIT, если она объявлена
            if 'FINDEXIT' in self.funcs:
                self._exec(('function_call', 'FINDEXIT', []))

        except RuntimeErrorRobot as e:
            print(f"Ошибка робота: {e}")
