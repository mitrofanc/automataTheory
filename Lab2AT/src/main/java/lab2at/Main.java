package lab2at;

import lab2at.ast.NodeType;
import lab2at.dfa.DFABuilder;
import lab2at.dfa.DFAState;
import lab2at.dfa.TreeAnalyzer;
import lab2at.lexer.Lexer;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.util.GraphVizRenderer;

import java.util.List;

/**
 * Демка: парсим регулярку, рисуем AST и DFA, печатаем их в консоль.
 */
public class Main {
    public static void main(String[] args) throws Exception {
        String pattern = "(<digit>0|1){3}?<digit>";

        // 1) Лексим и парсим AST
        Lexer lex    = new Lexer(pattern);
        Node  tree   = new RegexParser(lex.scan()).parse();

        // 2) Добавляем символ конца ввода
        Node eof     = new Node(NodeType.LITERAL, "#");
        tree         = new Node(NodeType.CONCAT, tree, eof);

        // 3) **Сначала** инициализируем все поля nullable/first/last/pos/follow
        TreeAnalyzer annot = new TreeAnalyzer();
        annot.analyze(tree);

        // 4) Только теперь — печатаем и рисуем AST с __готовыми__ полями
        System.out.println("=== AST with positions & annotations ===");
        System.out.println(tree);                        // если toString() выведет новые поля
        GraphVizRenderer.renderAst(tree, "ast.png");

        // 5) Строим и рисуем DFA как прежде
        DFABuilder b   = new DFABuilder(tree, annot.follow);
        List<DFAState> dfa = b.build();

        System.out.println("\n=== DFA ===");
        dfa.forEach(s -> System.out.println(s));

        GraphVizRenderer.renderDfa(dfa, "dfa.png");
    }

}

