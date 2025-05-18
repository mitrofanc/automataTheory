package lab2at;

import lab2at.lib.RegexLib;
import lab2at.util.GraphVizRenderer;
import java.io.IOException;
import java.util.List;

public class Main {

    public static void main(String[] args) throws IOException, InterruptedException {
        // Пример 1: L1 = a... (a*)  и  L2 = "aa"
        RegexLib lib1 = RegexLib.compile("a...(b|c)");
        GraphVizRenderer.renderAllDfas(lib1.getAllDFA(), "out/dfa1");
        RegexLib lib2 = RegexLib.compile("(a|b)...c");
        GraphVizRenderer.renderAllDfas(lib2.getAllDFA(), "out/dfa2");
        RegexLib inter1 = lib1.intersect(lib2);
        GraphVizRenderer.renderAllDfas(List.of(inter1.getAllDFA().get(inter1.getMainDFAId())), "out/intersect");


        System.out.println(inter1.match("aa"));    // true  (пересечение = {"aa"})
        System.out.println(inter1.match("a"));     // false
        System.out.println(inter1.match("aaaa"));  // false

        // Пример 2: L3 = a|b  и  L4 = b|c
        RegexLib lib3 = RegexLib.compile("a|b");
        RegexLib lib4 = RegexLib.compile("b|c");
        RegexLib inter2 = lib3.intersect(lib4);

        System.out.println(inter2.match("b"));     // true
        System.out.println(inter2.match("a"));     // false
        System.out.println(inter2.match("c"));     // false
    }


}
