package lab2at.dfa;

import lab2at.ast.*;
import lombok.Getter;
import java.util.*;

public final class DFACompiler {
    private final Map<String, Node> groupDefs;
    @Getter
    private final Map<String, Integer> nameToDfa = new HashMap<>(); // id для групп
    @Getter
    private final List<List<DFAState>> all = new ArrayList<>(); // список скомпилированных ДКА

    public DFACompiler(Map<String,Node> defs) {
        this.groupDefs = defs;
    }

    public int compile(Node mainAst) {
        for (var e : groupDefs.entrySet()) {
            if (!nameToDfa.containsKey(e.getKey())) {
                int gId = build(e.getValue());
                nameToDfa.put(e.getKey(), gId);
            }
        }
        return build(mainAst);
    }

    private int build(Node root) {
        if (!hasEndMarker(root)) {
            root = new Node(NodeType.CONCAT, root, new Node(NodeType.LITERAL, "#", null, null));
        }
        Numeration num = new Numeration();
        number(root, num);
        new TreeAnalyzer(num.followPos).analyze(root);
        List<DFAState> states = createDFA(root, num);
        states = DFAMinimizer.minimize(states);
        int id = all.size();
        all.add(states);
        return id;
    }

    private static boolean hasEndMarker(Node n) {
        return n.type == NodeType.CONCAT
                && n.right != null
                && n.right.type == NodeType.LITERAL
                && "#".equals(n.right.text);
    }

    private static class Numeration {
        int next = 1; // следующая свободная позиция
        int endPos = -1; // позиция '#'
        List<BitSet> followPos = new ArrayList<>(); // followpos для каждой node
        Map<Integer, Character> posToSym = new HashMap<>();
        Map<Integer, Integer> posToGroup = new HashMap<>();
    }

    private void number(Node n, Numeration numeration) {
        if (n.left!=null)  number(n.left, numeration);
        if (n.right!=null) number(n.right, numeration);

        if (n.type == NodeType.LITERAL || n.type == NodeType.GROUP_CALL) {
            n.pos = numeration.next++; // даем номер позиции
            while (numeration.followPos.size() <= n.pos) numeration.followPos.add(new BitSet());

            if (n.type == NodeType.LITERAL) {
                char c = n.text.charAt(0);
                numeration.posToSym.put(n.pos, c);
                if (c == '#') {
                    numeration.endPos = n.pos;
                }
            } else {                       // GROUP_CALL
                int groupID = nameToDfa.get(n.text);
                numeration.posToGroup.put(n.pos, groupID);
            }
        }
    }

    private List<DFAState> createDFA(Node root, Numeration numeration) {
        List<DFAState> dfaStates = new ArrayList<>();
        Map<BitSet, Integer> setToStateId = new HashMap<>(); // позиции, которые описывают состояние автомата
        Queue<BitSet> queue = new ArrayDeque<>();

        // первое состояние
        BitSet startSet = root.first;
        setToStateId.put((BitSet) startSet.clone(), 0);
        queue.add(startSet);

        while (!queue.isEmpty()) {
            BitSet currentSet = queue.remove();

            Map<Character, BitSet> moveBySymbol = new HashMap<>(); // переходы по символу
            Map<Integer, BitSet> moveByGroup = new HashMap<>(); // переходы по группе

            for (int p = currentSet.nextSetBit(0); p >= 0; p = currentSet.nextSetBit(p + 1)) {

                if (p == numeration.endPos)
                    continue;

                BitSet followPosFromCurSet = numeration.followPos.get(p);

                if (numeration.posToSym.containsKey(p)) {      // символ
                    char symbol = numeration.posToSym.get(p);
                    moveBySymbol.computeIfAbsent(symbol, k -> new BitSet()).or(followPosFromCurSet); // объединяем
                } else if (numeration.posToGroup.containsKey(p)) { // если группа
                    int groupId = numeration.posToGroup.get(p);
                    moveByGroup.computeIfAbsent(groupId, k -> new BitSet()).or(followPosFromCurSet); // объединяем
                }
            }

            // переход по символу
            Map<Character, Integer> transBySymbol = new HashMap<>();
            for (var e : moveBySymbol.entrySet()) {
                char symbol = e.getKey();
                BitSet targetSet = e.getValue();
                int targetId = getStateId(targetSet, setToStateId, queue);
                transBySymbol.put(symbol, targetId);
            }

            // переход по группе
            Map<Integer, Integer> transByGroup = new HashMap<>();
            for (var e : moveByGroup.entrySet()) {
                int groupId = e.getKey();
                BitSet targetSet = e.getValue();
                int targetId = getStateId(targetSet, setToStateId, queue);
                transByGroup.put(groupId, targetId);
            }

            boolean accept = numeration.endPos >= 0 && currentSet.get(numeration.endPos);

            dfaStates.add(new DFAState(
                    (BitSet) currentSet.clone(),
                    accept,
                    transBySymbol,
                    transByGroup)
            );
        }

        return dfaStates;
    }

    // проверяет существует ли данное состояние, если нет, то создает его
    private int getStateId(BitSet posSet, Map<BitSet,Integer> setToStateId, Queue<BitSet> queue) {
        Integer exist = setToStateId.get(posSet);
        if (exist != null) {
            return exist;
        } else {
            int newId = setToStateId.size();
            setToStateId.put((BitSet) posSet.clone(), newId);
            queue.add(posSet);
            return newId;
        }
    }
}
