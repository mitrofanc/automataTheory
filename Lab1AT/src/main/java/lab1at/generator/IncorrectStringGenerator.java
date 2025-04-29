package lab1at.generator;

import java.util.Random;

public class IncorrectStringGenerator implements StringGenerator {
    public static final Random RANDOM = new Random();

    @Override
    public String generateString(int nameLen, int parameterNum) {
        String correct = new CorrectStringGenerator().generateString(nameLen, parameterNum);

        int errorType = RANDOM.nextInt(3);

        switch (errorType) {
            case 0: // ошибка типа функции
                String invalidType = generateRandomString(RANDOM.nextInt(3) + 3);
                int firstSpace = correct.indexOf(" ");
                return invalidType + correct.substring(firstSpace);

            case 1: // ошибка в названии функции
                int space = correct.indexOf(" ");
                int startParams = correct.indexOf("(");
                String invalidFuncName = RANDOM.nextInt(10)
                        + generateRandomString(startParams - space + 1);
                return correct.substring(0, space + 1) + invalidFuncName + correct.substring(startParams);

            case 2: // ошибка в параметрах
                int openParenIndex = correct.indexOf("(");
                int closeParenIndex = correct.indexOf(")");
                String params = correct.substring(openParenIndex + 1, closeParenIndex).trim();
                if (!params.isEmpty()) {
                    String[] paramArray = params.split("\\s*,\\s*");
                    String firstParam = paramArray[0];
                    int spaceIndex = firstParam.indexOf(" ");
                    int error = RANDOM.nextInt(2); // 0 - тип, 1 - имя
                    String invalidParam;
                    if (error == 0) { // неправильный тип
                        String invalidParamType = generateRandomString(RANDOM.nextInt(3) + 3);
                        String paramName = firstParam.substring(spaceIndex + 1);
                        invalidParam = invalidParamType + " " + paramName;
                    } else { // неправильное название
                        String paramType = firstParam.substring(0, spaceIndex);
                        String invalidParamName = RANDOM.nextInt(10)
                                + generateRandomString(firstParam.length() - spaceIndex + 1);
                        invalidParam = paramType + " " + invalidParamName;
                    }

                    paramArray[0] = invalidParam;
                    StringBuilder newParams = new StringBuilder();
                    for (int i = 0; i < paramArray.length; i++) {
                        if (i > 0) {
                            newParams.append(", ");
                        }
                        newParams.append(paramArray[i]);
                    }

                    return correct.substring(0, openParenIndex + 1) +
                            newParams.toString() +
                            correct.substring(closeParenIndex);
                }
                break;

            default:
                return correct.substring(0, correct.length() - 1);
        }
        return correct;
    }

    private String generateRandomString(int length) {
        String alphabet = Constants.LOWERCASE + Constants.UPPERCASE;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < length; i++) {
            sb.append(alphabet.charAt(RANDOM.nextInt(alphabet.length())));
        }
        return sb.toString();
    }
}
