package lab2at;

import lab2at.dfa.DFARunner;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.ast.NodeType;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFAState;
import lab2at.util.GraphVizRenderer;

import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        String pattern = "abc?(<name1>lo|l)(t{3})%?%...<name1>";
        String input   = "0101";

        // 1) Лексим
        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();

        // 2) Парсим AST (еще без конца-маркера)
        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();
        System.out.println("AST before end-marker: " + ast);

        System.out.println("AST with end-marker: " + ast);
        GraphVizRenderer.renderAst(ast,           "out/ast_start.png");

        // 4) Компилируем recursive-DFA (сначала под-группы, потом главный)
        Map<String, Node> defs = parser.getGroupDefs();
        DFACompiler compiler = new DFACompiler(defs);
        int mainDfaId = compiler.compile(ast);
        List<List<DFAState>> allDfas = compiler.getAll();

        // 5) Рисуем AST и все DFA (включая вложенные)
        GraphVizRenderer.renderAst(ast,           "out/ast.png");
        GraphVizRenderer.renderAllDfas(allDfas,  "out/dfa");

//        // 6) Запускаем matcher и проверяем ввод
//        DFARunner runner = new DFARunner(allDfas);
//        boolean matches = runner.matches(input, mainDfaId);
//        System.out.printf("Input \"%s\" matches? %s%n", input, matches);
    }
}
