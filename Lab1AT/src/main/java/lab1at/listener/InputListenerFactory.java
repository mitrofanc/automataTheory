package lab1at.listener;

import java.util.Scanner;

public class InputListenerFactory {
    public static InputListener createListener() {
        Scanner scanner = new Scanner(System.in);
        System.out.println("Choose the source: 1 - file, 2 - CL:");
        String choice = scanner.nextLine();
        if ("1".equals(choice)) {
            return new InputListenerFile();
        } else {
            return new InputListenerCL();
        }
    }
}
