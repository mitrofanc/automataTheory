package lab2at.util;

import lab2at.ast.Node;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

// Визуализация AST через GraphViz
public class GraphVizRenderer {

    public static void render(Node root, String imageOutPath) throws IOException, InterruptedException {
        String dot = toDot(root);

        // Пишем её во временный файл
        Path dotPath = Paths.get("ast.dot");
        Files.writeString(dotPath, dot);

        // Запускаем GraphViz
        Process p = new ProcessBuilder("dot", "-Tpng",
                dotPath.toString(),
                "-o", imageOutPath)
                .inheritIO()
                .start();
        int code = p.waitFor();
        if (code != 0) {
            throw new RuntimeException("GraphViz returned non-zero code " + code);
        }
        System.out.println("AST image generated at: " + imageOutPath);
    }

    // Преобразует AST в строку в формате DOT
    public static String toDot(Node root) {
        StringBuilder sb = new StringBuilder();
        sb.append("digraph AST {\n");
        sb.append("  node [shape=circle, fontname=\"Courier\"];\n");

        Map<Node,String> ids = new IdentityHashMap<>();
        AtomicInteger counter = new AtomicInteger(0);
        buildDot(root, sb, ids, counter);

        sb.append("}\n");
        return sb.toString();
    }

    // Рекурсивно обходит узлы, присваивая каждому уникальный ID
    private static void buildDot(Node node, StringBuilder sb, Map<Node,String> ids, AtomicInteger counter) {
        String id = "n" + counter.getAndIncrement();
        ids.put(node, id);

        // текст метки: тип узла + (если есть) перенос + текст
        String label = node.type.name()
                + (node.text != null ? "\\n" + node.text : "");
        sb.append(String.format("  %s [label=\"%s\"];\n", id, label));

        // левый ребёнок
        if (node.left != null) {
            buildDot(node.left, sb, ids, counter);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(node.left)));
        }
        // правый ребёнок
        if (node.right != null) {
            buildDot(node.right, sb, ids, counter);
            sb.append(String.format("  %s -> %s;\n", id, ids.get(node.right)));
        }
    }
}
