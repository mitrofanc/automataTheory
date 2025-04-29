package lab1at.output;

import java.util.Scanner;

public class OutputFactory {
    public static Output createOutput() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Choose type of output: 1 - file, 2 - CL:");
        String choice = scanner.nextLine();
        if ("1".equals(choice)) {
            System.out.println("Input the name of output file:");
            String fileName = scanner.nextLine();
            return new OutputFile(fileName);
        } else {
            return new OutputCL();
        }
    }
}
