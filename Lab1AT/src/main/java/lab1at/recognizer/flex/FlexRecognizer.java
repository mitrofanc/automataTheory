package lab1at.recognizer.flex;
import lab1at.recognizer.RecognitionResult;
import lab1at.recognizer.Recognizer;

import java.io.IOException;
import java.io.StringReader;

public class FlexRecognizer implements Recognizer {

    @Override
    public RecognitionResult recognize(String str) {
        if (str == null || str.isEmpty()) {
            return new RecognitionResult(false, null);
        }

        try {
            Lexer lexer = new Lexer(new StringReader(str));
            if (lexer.yylex() == 0) return new RecognitionResult(true, lexer.getFuncName());
            else return new RecognitionResult(false, null);
        } catch (IOException e) {
            return new RecognitionResult(false, null);
        }

    }
}
