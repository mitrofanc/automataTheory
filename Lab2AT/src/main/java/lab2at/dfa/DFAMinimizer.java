package lab2at.dfa;

import java.util.*;

public final class DFAMinimizer {

    private DFAMinimizer(){}

    public static List<DFAState> minimize(List<DFAState> raw) {

        int n = raw.size();
        int[] old2new = new int[n];
        Arrays.fill(old2new, -1);

        List<DFAState> dst = new ArrayList<>();
        for (int q = 0; q < n; q++) {
            if (old2new[q] != -1) continue;          // уже куда-то склеили

            old2new[q] = dst.size();                 // номер нового состояния
            for (int r = q + 1; r < n; r++) {
                if (old2new[r] != -1) continue;
                if (eq(raw.get(q), raw.get(r), old2new)) {
                    old2new[r] = old2new[q];         // склеиваем r к q
                }
            }
            dst.add(null);                           // зарезервировали место
        }

        for (int q = 0; q < n; q++) {
            int newId = old2new[q];
            if (dst.get(newId) != null) continue;    // уже заполнили

            DFAState src = raw.get(q);
            Map<Character,Integer> ch = new HashMap<>();
            for (var e : src.charTrans().entrySet())
                ch.put(e.getKey(), old2new[e.getValue()]);

            Map<Integer,Integer> gr = new HashMap<>();
            for (var e : src.groupTrans().entrySet())
                gr.put(e.getKey(), old2new[e.getValue()]);

            dst.set(newId, new DFAState(
                    (BitSet)src.positions().clone(),
                    src.accept(), ch, gr));
        }
        return dst;
    }

    private static boolean eq(DFAState a, DFAState b, int[] old2new) {
        if (a.accept() != b.accept()) return false;
        if (!a.charTrans().keySet().equals(b.charTrans().keySet())) return false;
        if (!a.groupTrans().keySet().equals(b.groupTrans().keySet())) return false;

        for (var e : a.charTrans().entrySet()) {
            int toA = e.getValue(), toB = b.charTrans().get(e.getKey());
            if (mapped(toA, old2new) != mapped(toB, old2new)) return false;
        }
        for (var e : a.groupTrans().entrySet()) {
            int toA = e.getValue(), toB = b.groupTrans().get(e.getKey());
            if (mapped(toA, old2new) != mapped(toB, old2new)) return false;
        }
        return true;
    }

    private static int mapped(int old, int[] map){
        return map[old] == -1 ? old : map[old];   // если уже слит – берём новое id
    }
}
