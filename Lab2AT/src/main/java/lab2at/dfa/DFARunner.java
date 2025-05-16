package lab2at.dfa;

import java.util.*;

public final class DFARunner {
    private final List<List<DFAState>> all;

    public DFARunner(List<List<DFAState>> all) {
        this.all = all;
    }

    public boolean matches(String str, int mainId) {
        record Frame(int dfa, int st) {}

        int dfa = mainId; // текущий ДКА
        int st = 0; // текущее состояние
        int i = 0; // позиция в строке
        Deque<Frame> stack = new ArrayDeque<>();

        while (true) {
            DFAState curState = all.get(dfa).get(st);

            // по символу
            if (i < str.length()) {
                char c = str.charAt(i);
                Integer next = curState.charTrans().get(c);
                if (next != null) {
                    st = next;
                    i++;
                    continue;
                }
            }

            // по группе
            if (!curState.groupTrans().isEmpty()) {
                var e = curState.groupTrans().entrySet().iterator().next();
                int subDFA = e.getKey();
                int returnSt = e.getValue();
                stack.push(new Frame(dfa, returnSt)); // куда вернутся
                dfa = subDFA;
                st  = 0;
                continue;
            }

            // принимающее?
            if (curState.accept()) {
                if (!stack.isEmpty()) {
                    Frame f = stack.pop();
                    dfa = f.dfa();
                    st = f.st();
                    continue;
                }
                return i == str.length();
            }
            return false;
        }
    }

    public int matchPrefix(String str, int from, int mainId) {
        record Frame(int dfa, int st) {}

        int dfa = mainId; // текущий ДКА
        int st = 0; // текущее состояние
        int i = 0; // позиция в строке
        Deque<Frame> stack = new ArrayDeque<>();

        while (true) {
            DFAState curState = all.get(dfa).get(st);

            // по символу
            if (i < str.length()) {
                Integer next = curState.charTrans().get(str.charAt(i));
                if (next != null) {
                    st = next;
                    i++;
                    continue;
                }
            }

            // по группе
            if (!curState.groupTrans().isEmpty()) {
                var e = curState.groupTrans().entrySet().iterator().next();
                stack.push(new Frame(dfa, e.getValue()));
                dfa = e.getKey();
                st = 0;
                continue;
            }

            // принимающее?
            if (curState.accept()) {
                if (stack.isEmpty())
                    return i - from; // длина совпадения
                Frame f = stack.pop(); // завершаем под-DFA
                dfa = f.dfa();
                st = f.st();
                continue;
            }
            return -1; // матч невозможен
        }
    }
}
