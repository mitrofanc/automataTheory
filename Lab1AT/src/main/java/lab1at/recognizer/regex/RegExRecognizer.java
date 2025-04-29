package lab1at.recognizer.regex;

import lab1at.recognizer.RecognitionResult;
import lab1at.recognizer.Recognizer;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegExRecognizer implements Recognizer {

    private static final String TYPE = "(?:int|short|long)";
    private static final String NAME = "[a-zA-Z][a-zA-Z0-9]{0,15}";
    private static final String PARAM = TYPE + "\\s+" + NAME;
    private static final String PARAMS_REGEX = "(?:" + PARAM + "(?:\\s*,\\s*" + PARAM + ")*)?";
    private static final String FUNC_REGEX =
            "^\\s*" +
            "(" + TYPE + ")" +
            "\\s+" +
            "(" + NAME + ")" +
            "\\s*\\(" +
            "\\s*" +
            "(" + PARAMS_REGEX + ")" +
            "\\s*\\)" +
            "\\s*;" +
            "\\s*$";

    private static final Pattern funcPattern = Pattern.compile(FUNC_REGEX);

    private static final String SINGLE_PARAM_REGEX = "^\\s*(" + TYPE + ")\\s+(" + NAME + ")\\s*$";
    private static final Pattern singleParamPattern = Pattern.compile(SINGLE_PARAM_REGEX);

    @Override
    public RecognitionResult recognize(String str) {
        if (str == null || str.isEmpty())
            return new RecognitionResult(false, null);

        Matcher matcher = funcPattern.matcher(str);
        if (matcher.matches()) {
            String funcName = matcher.group(2);
            return new RecognitionResult(true, funcName);
        } else return new RecognitionResult(false, null);
    }

}
