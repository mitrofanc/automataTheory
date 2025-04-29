package lab1at.recognizer.smc;

import lab1at.recognizer.RecognitionResult;
import lab1at.recognizer.Recognizer;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class AppClass implements Recognizer {
    private final StateMapContext _fsm;

    private boolean moreParamsNeed;

    private boolean isAcceptable;

    private String funcName;

    public AppClass() {
        _fsm = new StateMapContext(this);
        isAcceptable = false;
        moreParamsNeed = false;
    }

    public void setFuncName(String funcName) {
        this.funcName = funcName;
    }

    public static boolean isType(String str) {
        return "int".equals(str) || "short".equals(str) || "long".equals(str);
    }

    public static boolean isName(String str) {
        return str != null && str.matches("[a-zA-Z][a-zA-Z0-9]{0,15}");
    }

    public void acceptable() {
        isAcceptable = true;
    }

    public void unacceptable() {
        isAcceptable = false;
    }

    public boolean getMoreParamsNeed() {
        return moreParamsNeed;
    }

    public void moreParamsNeeded() {
        moreParamsNeed = true;
    }

    public void noMoreParamsNeeded() {
        moreParamsNeed = false;
    }

    public boolean isString(String str) {
        return true;
    }

    private List<String> tokenize(String str) { // метод next, iterable
        List<String> tokens = new ArrayList<>();
        int tokenStart = -1; // токен ещё не начат

        for (int i = 0; i < str.length(); i++) {
            char ch = str.charAt(i);
            if (Character.isLetterOrDigit(ch) || ch == '_') {
                if (tokenStart == -1) {
                    tokenStart = i;
                }
            } else {
                if (tokenStart != -1) {
                    tokens.add(str.substring(tokenStart, i));
                    tokenStart = -1;
                }
                if (!Character.isWhitespace(ch)) {
                    tokens.add(String.valueOf(ch));
                }
            }
        }
        if (tokenStart != -1) {
            tokens.add(str.substring(tokenStart));
        }
        return tokens;
    }

    @Override
    public RecognitionResult recognize(String str) {
        if (str == null || str.isEmpty())
            return new RecognitionResult(false, null);

        List<String> tokens = tokenize(str);
        _fsm.emptyStateStack();
        _fsm.setState(StateMapContext.Map1.Start);
        _fsm.enterStartState();
        for (String token : tokens) {
            _fsm.Move(token);
            if(_fsm.getState().getId() == 8) break;
        }
        _fsm.EOS();
        if (isAcceptable) {
            return new RecognitionResult(true, funcName);
        } else return new RecognitionResult(false, null);
}
}
