package lab2at.dfa;

import java.util.*;

public final class DFARunner {
    private final List<List<DFAState>> all;

    public DFARunner(List<List<DFAState>> all) {
        this.all = all;
    }

    public static final class PrefixMatch {
        public int length; //  –1, если не совпало
        public final Map<Integer, int[]> namedGroupSubs = new HashMap<>(); // dfaId, [start, end]
    }

    public PrefixMatch matchPrefix(String str, int from, int mainId) {
        record Frame(int dfa, int retSt, int groupId, int groupStart) {}

        Deque<Frame> stack = new ArrayDeque<>();
        PrefixMatch prefixMatch = new PrefixMatch();
        prefixMatch.length = -1;

        int dfa = mainId;
        int st = 0;
        int i = from;

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
                int subId = e.getKey();
                int retSt = e.getValue(); // куда вернуться
                stack.push(new Frame(dfa, retSt, subId, i - from));
                prefixMatch.namedGroupSubs.put(subId, new int[]{i - from, -1});

                dfa = subId;
                st = 0;
                continue;
            }

            // принимающее?
            if (curState.accept()) {
                if (!stack.isEmpty()) {
                    var frame = stack.pop();
                    prefixMatch.namedGroupSubs.get(frame.groupId)[1] = i - from; // ставим окончание
                    dfa = frame.dfa;
                    st = frame.retSt;
                    continue;
                }
                prefixMatch.length = i - from;
                return prefixMatch;
            }

           // не распознали
            return prefixMatch;
        }
    }
}
