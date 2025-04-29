package lab1at.generator;

import java.util.Random;

public class CorrectStringGenerator implements StringGenerator{
    public static Random RANDOM = new Random();


    @Override
    public String generateString(int nameLen, int parameterNum) {
        String type = Constants.TYPES[RANDOM.nextInt(Constants.TYPES.length)];
        String funcName = generateName(nameLen);
        StringBuilder paramsBuilder = new StringBuilder();
        for (int i = 0; i < parameterNum; i++) {
            if (i > 0) {
                paramsBuilder.append(", ");
            }
            String paramType = Constants.TYPES[RANDOM.nextInt(Constants.TYPES.length)];
            String paramName = generateName(nameLen);
            paramsBuilder.append(paramType).append(" ").append(paramName);
        }
        return type + " " + funcName + "(" + paramsBuilder.toString() + ");";
    }


    public static String generateName(int length) {
        if (length < 1) {
            throw new IllegalArgumentException("Name length must > 0");
        }
        String alphabet = Constants.LOWERCASE + Constants.UPPERCASE;
        StringBuilder sb = new StringBuilder();
        sb.append(alphabet.charAt(RANDOM.nextInt(alphabet.length())));
        for (int i = 1; i < length; i++) {
            sb.append((alphabet + Constants.NUM).charAt(RANDOM.nextInt((alphabet + Constants.NUM).length())));
        }
        return sb.toString();
    }
}
