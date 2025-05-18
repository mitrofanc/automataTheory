package lab2at.dfa;

import lab2at.ast.Node;
import lab2at.ast.NodeType;

import java.util.*;

public final class DFAOperations {

    private DFAOperations() {}

    public static Node reverse(Node n) {
        if (n == null) return null;

        if (n.type == NodeType.LITERAL || n.type == NodeType.GROUP_CALL)
            return new Node(n.type, n.text, null, null);

        Node a = reverse(n.left);
        Node b = reverse(n.right);

        return switch (n.type) {
            case CONCAT -> new Node(NodeType.CONCAT, b, a);
            case OR -> new Node(NodeType.OR, a, b);
            case KLEENE,
                 OPTIONAL,
                 NULL_REPEAT -> new Node(n.type,  a, null);
            default -> throw new IllegalStateException("Unexpected: " + n.type);
        };
    }

    public static List<DFAState> intersect(List<DFAState> dfa1, List<DFAState> dfa2) {
        Map<Pair<Integer, Integer>, Integer> stateMap = new HashMap<>(); // (i, j) -> newState
        List<DFAState> result = new ArrayList<>();
        Queue<Pair<Integer, Integer>> queue = new ArrayDeque<>();

        // инициализация
        Pair<Integer, Integer> start = new Pair<>(0, 0);
        stateMap.put(start, 0);
        queue.add(start);

        while (!queue.isEmpty()) {
            Pair<Integer, Integer> current = queue.poll();
            int id = stateMap.get(current);

            DFAState s1 = dfa1.get(current.first());
            DFAState s2 = dfa2.get(current.second());

            // принимающее состояние, если оба принимают
            boolean accept = s1.accept() && s2.accept();

            Map<Character, Integer> charTrans = new HashMap<>();
            Map<Integer, Integer> groupTrans = new HashMap<>();

            // все символы из обоих DFA
            Set<Character> allChars = new HashSet<>();
            allChars.addAll(s1.charTrans().keySet());
            allChars.addAll(s2.charTrans().keySet());

            // по символу
            for (char c : allChars) {
                Integer to1 = s1.charTrans().get(c);
                Integer to2 = s2.charTrans().get(c);
                if (to1 != null && to2 != null) {
                    Pair<Integer, Integer> next = new Pair<>(to1, to2);
                    int nextId = stateMap.computeIfAbsent(next, k -> {
                        queue.add(k);
                        return result.size() + queue.size();
                    });
                    charTrans.put(c, nextId);
                }
            }

            // по группам
            Set<Integer> allGroups = new HashSet<>();
            allGroups.addAll(s1.groupTrans().keySet());
            allGroups.addAll(s2.groupTrans().keySet());

            for (int g : allGroups) {
                Integer to1 = s1.groupTrans().get(g);
                Integer to2 = s2.groupTrans().get(g);
                if (to1 != null && to2 != null) {
                    Pair<Integer, Integer> next = new Pair<>(to1, to2);
                    int nextId = stateMap.computeIfAbsent(next, k -> {
                        queue.add(k);
                        return result.size() + queue.size();
                    });
                    groupTrans.put(g, nextId);
                }
            }

            result.add(new DFAState(s1.positions(), accept, charTrans, groupTrans));
        }

        return result;
    }

    private record Pair<F, S>(F first, S second) {}
}
