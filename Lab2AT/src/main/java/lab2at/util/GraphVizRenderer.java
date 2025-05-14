package lab2at.util;

import lab2at.ast.Node;
import lab2at.dfa.DFAState;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public final class GraphVizRenderer {
    private GraphVizRenderer() {}

    public static void renderAst(Node root, String outPng) throws IOException, InterruptedException {
        Path png = Paths.get(outPng);
        Files.createDirectories(png.getParent());
        String dot = toDotAst(root);
        Path dotFile = png.resolveSibling(png.getFileName() + ".dot");
        Files.writeString(dotFile, dot);
        runDot(dotFile, png);
        System.out.println("AST → " + png);
    }

    private static String toDotAst(Node root) {
        StringBuilder sb = new StringBuilder();
        sb.append("digraph AST {\n")
                .append("  node [shape=circle,fontname=\"Courier\"];\n");
        Map<Node,String> ids = new IdentityHashMap<>();
        AtomicInteger ctr = new AtomicInteger();
        buildDotAst(root, sb, ids, ctr);
        sb.append("}\n");
        return sb.toString();
    }

    private static void buildDotAst(Node n, StringBuilder sb,
                                    Map<Node,String> ids,
                                    AtomicInteger ctr) {
        String id = "n" + ctr.getAndIncrement();
        ids.put(n, id);

        StringBuilder lbl = new StringBuilder(n.type.name());
        if (n.text != null) lbl.append(":").append(n.text);
        lbl.append("\\npos=").append(n.pos);
        lbl.append("\\nnull=").append(n.nullable);
        lbl.append("\\nf=").append(n.first);
        lbl.append("\\nl=").append(n.last);

        sb.append(String.format("  %s [label=\"%s\"];\n", id, lbl));

        if (n.left != null) {
            buildDotAst(n.left, sb, ids, ctr);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(n.left)));
        }
        if (n.right != null) {
            buildDotAst(n.right, sb, ids, ctr);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(n.right)));
        }
    }

    public static void renderAllDfas(List<List<DFAState>> all, String outDir)
            throws IOException, InterruptedException {
        Path dir = Paths.get(outDir);
        Files.createDirectories(dir);

        for (int dfaId = 0; dfaId < all.size(); dfaId++) {
            List<DFAState> states = all.get(dfaId);
            String base = "dfa" + dfaId;
            Path dot  = dir.resolve(base + ".dot");
            Path png  = dir.resolve(base + ".png");

            Files.writeString(dot, toDotDfa(states, "U", dfaId));
            runDot(dot, png);
            System.out.println("DFA#" + dfaId + " → " + png);
        }
    }

    private static String toDotDfa(List<DFAState> states, String prefix, int dfaId) {
        StringBuilder sb = new StringBuilder();
        sb.append("digraph DFA_").append(dfaId).append(" {\n")
                .append("  rankdir=LR;\n")
                .append("  node [shape=circle,fontname=\"Courier\"];\n");

        // узлы
        for (int i = 0; i < states.size(); i++) {
            DFAState s = states.get(i);
            String shape = s.accept() ? "doublecircle" : "circle";
            sb.append(String.format("  %s%d [label=\"%s%d\" shape=%s];\n",
                    prefix, i, prefix, i, shape));
        }
        sb.append("\n");

        // рёбра по символам
        for (int i = 0; i < states.size(); i++) {
            DFAState s = states.get(i);
            for (var e : s.charTrans().entrySet()) {
                char c = e.getKey();
                int to = e.getValue();
                String lbl = escape(c);
                sb.append(String.format("  %s%d -> %s%d [label=\"%s\"];\n",
                        prefix, i, prefix, to, lbl));
            }
        }
        sb.append("\n");

        // рёбра по group-вызовам (пунктиром)
        for (int i = 0; i < states.size(); i++) {
            DFAState s = states.get(i);
            for (var e : s.groupTrans().entrySet()) {
                int gid = e.getKey();
                int to  = e.getValue();
                String lbl = "call_g" + gid;
                sb.append(String.format("  %s%d -> %s%d [style=dashed,label=\"%s\"];\n",
                        prefix, i, prefix, to, lbl));
            }
        }

        sb.append("}\n");
        return sb.toString();
    }

    private static void runDot(Path dotFile, Path pngFile)
            throws IOException, InterruptedException {
        Process p = new ProcessBuilder("dot","-Tpng",
                dotFile.toString(), "-o", pngFile.toString())
                .inheritIO()
                .start();
        if (p.waitFor() != 0) {
            throw new RuntimeException("dot exit code="+p.exitValue());
        }
    }

    private static String escape(char c) {
        return switch (c) {
            case '<','>','"','\\' -> "\\"+c;
            case ' '              -> "␣";
            default               -> String.valueOf(c);
        };
    }
}
