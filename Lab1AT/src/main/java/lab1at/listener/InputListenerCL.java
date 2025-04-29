package lab1at.listener;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class InputListenerCL implements InputListener {
    @Override
    public InputData getInput() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Input number of lines to parse:");
        int count = Integer.parseInt(scanner.nextLine());
        List<String> lines = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            System.out.println("Input string " + (i + 1) + ":");
            lines.add(scanner.nextLine());
        }
        System.out.println("Choose type of parser (regex/flex/smc):");
        String parserType = scanner.nextLine();
        return new InputData(lines, parserType);
    }
}
