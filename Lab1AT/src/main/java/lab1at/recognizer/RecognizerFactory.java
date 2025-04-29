package lab1at.recognizer;

import lab1at.recognizer.flex.FlexRecognizer;
import lab1at.recognizer.regex.RegExRecognizer;
import lab1at.recognizer.smc.AppClass;

public class RecognizerFactory {
    public static Recognizer createRecognizer(String type) {
        return switch (type) {
            case "flex" -> new FlexRecognizer();
            case "regex" -> new RegExRecognizer();
            case "smc" -> new AppClass();
            default -> throw new IllegalArgumentException("Unknown recognizer type: " + type);
        };
    }
}
