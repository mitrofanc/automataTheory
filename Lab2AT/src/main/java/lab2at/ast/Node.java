package lab2at.ast;

import java.util.BitSet;
import java.util.Objects;

public class Node {
    public final NodeType type;
    public String text;    // для литералов, именнованных групп, повторов
    public Node left, right;
    public int pos = -1; // >0 только у литерала и GROUPCALL
    public boolean nullable;
    public BitSet first = new BitSet();
    public BitSet last = new BitSet();
    public int repeatCount = -1; // только для повторов (отдельная логика для FP)
    // todo delete repeatCount

    public Node(NodeType type, String text) {
        this.type = Objects.requireNonNull(type);
        this.text = text;
    }

    public Node(NodeType type, Node left, Node right) {
        this(type, null);
        this.left = left;
        this.right = right;
    }

    public Node(NodeType type, String text, Node left, Node right) {
        this(type, text);
        this.left = left;
        this.right = right;
    }

    @Override
    public String toString() {
        String label = text == null ? type.name() : type.name() + ":" + text;
        if (left == null && right == null) {
            return label;
        }
        return "(" + label + " "
                + (left  == null ? "_" : left.toString()) + " "
                + (right == null ? "_" : right.toString()) + ")";
    }
}
