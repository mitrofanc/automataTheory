package astTests;

import lab2at.ast.Node;

import java.util.Objects;

// Рекурсивное сравнение двух AST
public final class AstAssert {
    public static boolean deepEquals(Node a, Node b) {
        if (a == b) return true;
        if (a == null || b == null) return false;

        return a.type == b.type &&
                Objects.equals(a.text,  b.text) &&
                deepEquals(a.left,  b.left) &&
                deepEquals(a.right, b.right);
    }

    // wrapper
    public static void assertAstEquals(Node expected, Node actual) {
        if (!deepEquals(expected, actual))
            throw new AssertionError("ASTs differ.\nexpected: "
                    + expected + "\nactual: " + actual);
    }

    private AstAssert() {}
}

