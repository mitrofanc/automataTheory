package lab2at.dfa;

import lab2at.ast.*;
import java.util.*;

public final class DFABuilder {

    private final Node root;
    private final List<BitSet> follow;
    private final Map<Integer, Character> posToSym = new HashMap<>();

    private int endPos = -1;

    public DFABuilder(Node root, List<BitSet> follow) {
        this.root   = root;
        this.follow = follow;
        createMapPosToSym(root);
    }

    // map(pos, lit)
    private void createMapPosToSym(Node n) {
        if (n.type == NodeType.LITERAL) {
            posToSym.put(n.pos, n.text.charAt(0));
            if ("#".equals(n.text)) {
                endPos = n.pos;
            }
        }
        if (n.left  != null) createMapPosToSym(n.left);
        if (n.right != null) createMapPosToSym(n.right);
    }


    public List<DFAState> build() {
        List<DFAState> states = new ArrayList<>(); // список состояний
        Map<BitSet, Integer> fpToStateIdx = new HashMap<>(); // FP->индекс состояния

        BitSet start = root.first; // init (bitset первый позиций)
        Queue<BitSet> q = new ArrayDeque<>(); // очередь для FP (по сути состояний)
        q.add(start);
        fpToStateIdx.put((BitSet) start.clone(), 0);

        // пока есть не пройденное состояние
        while (!q.isEmpty()) {
            BitSet S = q.remove();
            int id = fpToStateIdx.get(S); // берем индекс исходного

            Map<Character, BitSet> newSymSet = new HashMap<>(); // set, в котором собираем все возможные FP по каждому символу (map(sym, FP))
            for (int p = S.nextSetBit(0); p >= 0; p = S.nextSetBit(p+1)) { // по каждой позиции
                char c = posToSym.get(p);
                if (c =='#') continue;
                newSymSet.computeIfAbsent(c, k -> new BitSet()).or(follow.get(p));
            }

            // построение переходов
            Map<Character, Integer> trans = new HashMap<>();
            for (var a : newSymSet.entrySet()) {
                BitSet U = a.getValue(); // key: sym, val: FP
                Integer j = fpToStateIdx.get(U);
                if (j == null) { // если нет, создаем новое состояние
                    j = states.size() + q.size();
                    fpToStateIdx.put((BitSet) U.clone(), j);
                    q.add(U);
                }
                trans.put(a.getKey(), j); // S ->(a) U
            }

            boolean accept = endPos >= 0 && S.get(endPos);
//            states.add(id, new DFAState((BitSet) S.clone(), accept, trans));
        }
        return states;
    }
}
