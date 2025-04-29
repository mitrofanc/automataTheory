package lab1at.generator;

import lombok.experimental.UtilityClass;

@UtilityClass
public final class Constants {
    static final String[] TYPES = {"int", "short", "long"};
    static final String LOWERCASE = "abcdefghijklmnopqrstuvwxyz";
    static final String UPPERCASE = LOWERCASE.toUpperCase();
    static final String NUM = "0123456789";
}
