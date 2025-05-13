package lab2at.dfa;

import java.util.*;

/** Исполнение recursive-DFA со стеком возвратов. */
public final class DFARunner {
    private final List<List<DFAState>> all;

    public DFARunner(List<List<DFAState>> all) { this.all = all; }

    public boolean matches(String s, int mainId) {
        record Frame(int dfa,int st){}

        int dfa = mainId, st = 0, i = 0;
        Deque<Frame> stack = new ArrayDeque<>();

        while (true) {
            DFAState cur = all.get(dfa).get(st);

            // конец ввода
            if (i == s.length()) {
                if (cur.accept() && stack.isEmpty()) return true;
                if (cur.accept() && !stack.isEmpty()) {
                    Frame f = stack.pop();
                    dfa = f.dfa(); st = f.st();
                    continue;
                }
                return false;
            }

            char c = s.charAt(i);
            Integer nxt = cur.charTrans().get(c);
            if (nxt != null) {           // обычный символ
                st = nxt;
                i++;
                continue;
            }

            // пробуем групповой переход
            for (var e : cur.groupTrans().entrySet()) {
                int subId = e.getKey();
                int toAfter = e.getValue();
                stack.push(new Frame(dfa, toAfter));
                dfa = subId;
                st  = 0;
                // внимание: не считываем символы, просто переключаемся
                break;
            }
            if (dfa == cur.charTrans().size()) { // ни char, ни group
                return false;
            }
        }
    }
}
