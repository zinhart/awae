// Java code for serialization and deserialization
// of a Java object
import java.io.*;

public class SerialExample {

	public static void main(String[] args)
	{
		String filename = null;
        if (args.length == 1) {
			filename = args[0];
        }
        else {
            System.out.println("Usage <java SerialExample serial.ser>");
            System.exit(1);
        }
		DummyObject1 object = new DummyObject1("ab", 20, 2, 1000);


		// Serialization
		try {

			// Saving of object in a file
			FileOutputStream file = new FileOutputStream
										(filename);
			ObjectOutputStream out = new ObjectOutputStream
										(file);

			// Method for serialization of object
			out.writeObject(object);

			out.close();
			file.close();

			System.out.println("Object has been serialized\n"
							+ "Data before Deserialization.");
			DummyObject1.printdata(object);

			// value of static variable changed
			object.b = 2000;
		}

		catch (IOException ex) {
			System.out.println("IOException is caught");
		}
	}
}
