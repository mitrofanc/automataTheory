package lab2at.dfa;

import lab2at.ast.Node;

import java.util.BitSet;
import java.util.List;

public final class TreeAnalyzer {
    private final List<BitSet> followPos;

    public TreeAnalyzer(List<BitSet> followPos) {
        this.followPos = followPos;
    }

    public void analyze(Node n) {
        if (n.left  != null) analyze(n.left);
        if (n.right != null) analyze(n.right);

        switch (n.type) {
            case LITERAL, GROUP_CALL -> {
                n.nullable = false;
                n.first.set(n.pos);
                n.last.set(n.pos);
            }
            case NULL_REPEAT -> {
                n.nullable = true;
            }
            case CONCAT -> {
                n.nullable = n.left.nullable && n.right.nullable;

                if (n.left.nullable) { // если левая nullable, то берем из левой и правой
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
                    followPos.get(p).or(n.right.first);
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
                    followPos.get(p).or(n.first);
            }
            case OPTIONAL -> {
                n.nullable = true;
                n.first.or(n.left.first); // как у ребенка
                n.last.or(n.left.last); // как у ребенка
            }
            default -> throw new IllegalStateException("Unsupported node: " + n.type);
        }
    }
}
