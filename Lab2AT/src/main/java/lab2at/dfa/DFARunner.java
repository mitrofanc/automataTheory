package lab2at.dfa;

import java.util.*;

public final class DFARunner {
    private final List<List<DFAState>> all;

    public DFARunner(List<List<DFAState>> all) {
        this.all = all;
    }

    public boolean matches(String s, int mainId) {
        record Frame(int dfa, int st) {}

        int dfa = mainId; // текущий ДКА
        int st = 0; // текущее состояние
        int i = 0; // позиция в строке
        Deque<Frame> stack = new ArrayDeque<>();

        // true если съели символ
        boolean getSym = false;

        while (true) {
            DFAState curState = all.get(dfa).get(st);

            // переход по символу
            if (i < s.length()) {
                char c = s.charAt(i);
                Integer next = curState.charTrans().get(c);
                if (next != null) {
                    st = next;
                    i++;
                    getSym = true;
                    continue;
                }
            }

            // переход по группе
            if (getSym && !curState.groupTrans().isEmpty()) {
                for (var e : curState.groupTrans().entrySet()) {
                    int subDfa = e.getKey();
                    int returnSt = e.getValue();
                    stack.push(new Frame(dfa, returnSt)); // куда вернуться

                    dfa = subDfa;
                    st  = 0;
                    getSym = false;
                    break;
                }
                if (!getSym) continue;
            }

            // нет переходов, проверяем принимающее или нет
            if (curState.accept()) {
                if (stack.isEmpty()) return true; // главный ДКА

                Frame f = stack.pop();
                dfa = f.dfa();
                st  = f.st();
                getSym = true;
                continue;
            }
            return false;
        }
    }
}
