package lab2at;

import lab2at.dfa.DFARunner;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFAState;
import lab2at.util.GraphVizRenderer;

import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        // 1) Шаблон из задания
        String pattern = "abc?(<name1>lo|l)(t{3})%?%...<name1>";
        // 2) Входная строка, которая этому шаблону точно соответствует:
        //    a b [нет 'c'] → "ab"
        //    (<name1> lo|l) → "lo"
        //    (t{3})          → "ttt"
        //    %?%             → "?" (один знак вопроса)
        //    ...             → «нулевое или более» повторение этого «?» → здесь 0 повторов
        //    <name1>         → снова "lo"
        //
        //  Итого: "ablo ttt ? lo" без пробелов → "ablottt?lo"
        String input = "ablottt?lo";

        // 3) Лексим → Парсим → Смотрим AST
        Lexer lexer     = new Lexer(pattern);
        List<Token> tokens = lexer.scan();
        RegexParser parser = new RegexParser(tokens);
        Node ast           = parser.parse();
        System.out.println("AST: " + ast);

        // 4) Компилируем главный и под-DFA
        Map<String,Node> defs      = parser.getGroupDefs();
        DFACompiler     compiler   = new DFACompiler(defs);
        int              mainDfaId = compiler.compile(ast);
        List<List<DFAState>> all   = compiler.getAll();

        // 5) Проверяем
        DFARunner runner = new DFARunner(all);
        boolean ok = runner.matches(input, mainDfaId);
        System.out.printf("Input \"%s\" matches? %s%n", input, ok);

        // (опционально) визуализация
        GraphVizRenderer.renderAst(ast,        "out/ast.png");
        GraphVizRenderer.renderAllDfas(all,   "out/dfa");
    }
}
