package lab1at.listener;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class InputListenerFile implements InputListener {
    @Override
    public InputData getInput() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Input the name of the file:");
        String fileName = scanner.nextLine();
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                lines.add(line);
            }
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
        System.out.println("Choose type of parser (regex/flex/smc):");
        String parserType = scanner.nextLine();
        return new InputData(lines, parserType);
    }
}
