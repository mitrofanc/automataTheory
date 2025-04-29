package lab1at.output;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class OutputFile implements Output {

    private final String fileName;

    public OutputFile(String fileName) {
        this.fileName = fileName;
    }

    @Override
    public void display(String message) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(fileName))) {
            bw.write(message);
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
