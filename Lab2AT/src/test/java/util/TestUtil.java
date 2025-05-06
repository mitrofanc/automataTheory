package util;

import lab2at.ast.Node;
import lab2at.util.GraphVizRenderer;

import java.nio.file.Files;
import java.nio.file.Path;

public final class TestUtil {


    public static void renderTree(Node root, String name) {
        Path OUT_DIR = Path.of("src/test/java/astTests/trees");
        try {
//            Files.createDirectories(OUT_DIR);
            GraphVizRenderer.render(root, OUT_DIR.resolve(name + ".png").toString());
        } catch (Exception e) {
            System.err.println(e.getMessage());
        }
    }
    private TestUtil() {}
}

