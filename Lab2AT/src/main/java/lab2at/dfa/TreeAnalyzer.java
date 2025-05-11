package lab2at.dfa;

import lab2at.ast.Node;
import lab2at.ast.NodeType;

import java.util.ArrayList;
import java.util.BitSet;
import java.util.List;

public class TreeAnalyzer {
    public final List<BitSet> followpos = new ArrayList<>(); // FP
    private int nextPos = 1;    // нумерация листьев начинается с 1

    public void analyze(Node root) {
        numberLeaves(root);
        compute(root);                    // post‑order вычисление
    }

    // Нумеруем литералы
    private void numberLeaves(Node n) {
        if (n.left  != null) numberLeaves(n.left);
        if (n.right != null) numberLeaves(n.right);

        if (n.type == NodeType.LITERAL) {
            n.pos = nextPos++;
            while (followpos.size() <= n.pos)
                followpos.add(new BitSet()); // добавляем FP для каждого литерала
        }
    }

    private void compute(Node n) {
        if (n.left  != null) compute(n.left);
        if (n.right != null) compute(n.right);

        switch (n.type) {
            case LITERAL -> {
                n.nullable = false;
                n.first.set(n.pos);
                n.last.set(n.pos);
            }
            case CONCAT -> {
                n.nullable = n.left.nullable && n.right.nullable;

                if (n.left.nullable) { // если левая nullable, то берем из правой
                    n.first.or(n.left.first);
                    n.first.or(n.right.first);
                } else {
                    n.first.or(n.left.first);
                }

                if (n.right.nullable) { // аналогично
                    n.last.or(n.left.last);
                    n.last.or(n.right.last);
                } else {
                    n.last.or(n.right.last);
                }

                // для каждой позиции last(left) добавляем first(right)
                for (int p = n.left.last.nextSetBit(0); p >= 0; p = n.left.last.nextSetBit(p+1))
                     followpos.get(p).or(n.right.first);
            }
            case OR -> {
                n.nullable = n.left.nullable || n.right.nullable;
                n.first.or(n.left.first); n.first.or(n.right.first); // first = first(left) v first(right)
                n.last.or(n.left.last); n.last.or(n.right.last); // last = last(left) v last(right)
            }
            case KLEENE -> {
                n.nullable = true;
                n.first.or(n.left.first); // как у ребенка
                n.last.or(n.left.last); // как у ребенка
                // для каждой позиции last(left) добавляем весь first(left)
                for (int p = n.last.nextSetBit(0); p >= 0; p = n.last.nextSetBit(p+1))
                    followpos.get(p).or(n.first);
            }
            case OPTIONAL -> {
                n.nullable = true;
                n.first.or(n.left.first); // как у ребенка
                n.last.or(n.left.last); // как у ребенка
            }
            case GROUP_DEF -> {          // группа = содержимое
                n.nullable = n.left.nullable;
                n.first.or(n.left.first);
                n.last.or(n.left.last);
            }
            case GROUP_REF ->    {} // не участвует в построении автомата
            case NULL_REPEAT -> {
                n.nullable = true;
            }
            default -> throw new IllegalStateException("Unsupported node: "+n.type);
        }
    }
}
