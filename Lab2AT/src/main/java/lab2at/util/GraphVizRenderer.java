package lab2at.util;

import lab2at.ast.Node;
import lab2at.dfa.DFAState;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class GraphVizRenderer {

    public static void renderAst(Node root, String imageOutPath)
            throws IOException, InterruptedException {
        String dot = toDot(root);
        writeDotAndPng(dot, imageOutPath);
        System.out.println("AST image generated at: " + imageOutPath);
    }

    public static String toDot(Node root) {
        StringBuilder sb = new StringBuilder();
        sb.append("digraph AST {\n")
                .append("  node [shape=circle, fontname=\"Courier\"];\n");

        Map<Node,String> ids = new IdentityHashMap<>();
        AtomicInteger counter = new AtomicInteger(0);
        buildDot(root, sb, ids, counter);

        sb.append("}\n");
        return sb.toString();
    }

    private static void buildDot(Node node,
                                 StringBuilder sb,
                                 Map<Node,String> ids,
                                 AtomicInteger counter) {
        String id = "n" + counter.getAndIncrement();
        ids.put(node, id);

        // Формируем метку узла:
        // TYPE[:text]
        // pos=…
        // null=…
        // f=…
        // l=…
        StringBuilder label = new StringBuilder();
        label.append(node.type.name());
        if (node.text != null) {
            label.append(":").append(node.text);
        }
        label.append("\\npos=").append(node.pos);
        label.append("\\nnull=").append(node.nullable);
        label.append("\\nf=").append(bitSetToString(node.first));
        label.append("\\nl=").append(bitSetToString(node.last));

        sb.append(String.format("  %s [label=\"%s\"];\n", id, label));

        if (node.left != null) {
            buildDot(node.left, sb, ids, counter);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(node.left)));
        }
        if (node.right != null) {
            buildDot(node.right, sb, ids, counter);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(node.right)));
        }
    }

    private static String bitSetToString(BitSet bs) {
        return bs.toString();
    }

    public static void renderDfa(List<DFAState> states, String imageOutPath)
            throws IOException, InterruptedException {
        StringBuilder sb = new StringBuilder();
        sb.append("digraph DFA {\n")
                .append("  rankdir=LR;\n")
                .append("  node [shape=circle, fontname=\"Courier\"];\n");

        // узлы
        for (int i = 0; i < states.size(); i++) {
            DFAState st = states.get(i);
            String shape = st.accept() ? "doublecircle" : "circle";
            sb.append(String.format("  U%d [label=\"U%d\" shape=%s];\n",
                    i, i, shape));
        }

        // рёбра
        for (int i = 0; i < states.size(); i++) {
            DFAState st = states.get(i);
            for (var e : st.trans().entrySet()) {
                char sym = e.getKey();
                int to   = e.getValue();
                String lbl = sym == '"' ? "\\\"" : String.valueOf(sym);
                sb.append(String.format("  U%d -> U%d [label=\"%s\"];\n",
                        i, to, lbl));
            }
        }

        sb.append("}\n");
        writeDotAndPng(sb.toString(), imageOutPath);
        System.out.println("DFA image generated at: " + imageOutPath);
    }

    private static void writeDotAndPng(String dot, String imageOutPath)
            throws IOException, InterruptedException {
        Path dotPath = Paths.get(imageOutPath + ".dot");
        Files.writeString(dotPath, dot);

        Process p = new ProcessBuilder("dot", "-Tpng",
                dotPath.toString(),
                "-o", imageOutPath)
                .inheritIO()
                .start();
        int code = p.waitFor();
        if (code != 0) {
            throw new RuntimeException("GraphViz returned non-zero code " + code);
        }
    }

    private GraphVizRenderer() {}
}
