package lab2at.lib;

import lab2at.dfa.DFAState;
import java.util.*;

public final class ToRegex {
    private ToRegex() {}

    public static String toRegex(List<DFAState> states, Map<Integer, String> groupNames) {
        int n = states.size();
        int start = n;
        int end = n + 1;

        // R[from][to]
        Map<Integer, Map<Integer, StringBuilder>> R = new HashMap<>();
        for (int s = 0; s < n + 2; s++) {
            R.put(s, new HashMap<>());
        }

        // 1) оригинальные переходы
        for (int from = 0; from < n; from++) {
            DFAState st = states.get(from);
            // по символу
            for (var e : st.charTrans().entrySet()) {
                addEdge(R, from, e.getValue(), Character.toString(e.getKey()));
            }
            // по группе
            for (var e : st.groupTrans().entrySet()) {
                String tok = "<" + groupNames.get(e.getKey()) + ">";
                addEdge(R, from, e.getValue(), tok);
            }
        }

        // ε переходы
        addEdge(R, start, 0, "ε");
        for (int i = 0; i < n; i++) {
            if (states.get(i).accept()) {
                addEdge(R, i, end, "ε");
            }
        }

        // 3) список промежуточных вершин для удаления
        List<Integer> toDelete = new ArrayList<>();
        for (int stId = 0; stId < n + 2; stId++) {
            if (stId != start && stId != end) toDelete.add(stId);
        }

        // 4) state‐elimination
        for (int s : toDelete) {
            // s->s
            String loop = R.get(s).getOrDefault(s, new StringBuilder()).toString();
            String kleene = loop.isEmpty() ? "" : "(" + loop + ")..."; // обертка над петлей

            // для каждой пары p≠s, q≠s
            for (int p = 0; p < n + 2; p++) {
                if (p == s) continue;
                String rps = R.get(p).getOrDefault(s, new StringBuilder()).toString();
                if (rps.isEmpty()) continue;
                for (int q = 0; q < n + 2; q++) {
                    if (q == s) continue;
                    String rsq = R.get(s).getOrDefault(q, new StringBuilder()).toString();
                    if (rsq.isEmpty()) continue;
                    // объединяем: (rps)(loop...)(rsq)
                    String repl = rps + kleene + rsq;

                    addEdge(R, p, q, repl);
                }
            }

            R.get(s).clear();
            for (var row : R.values()) {
                row.remove(s);
            }
        }

        String out = R.get(start).get(end).toString().replaceAll("ε", "");

        return out.isEmpty() ? "empty" : out;
    }

    private static void addEdge(Map<Integer, Map<Integer, StringBuilder>> R, int from, int to, String expr) {
        Map<Integer, StringBuilder> row = R.get(from);
        StringBuilder sb = row.computeIfAbsent(to, k -> new StringBuilder());
        if (sb.length() > 0) sb.append("|");
        sb.append(expr);
    }
}
