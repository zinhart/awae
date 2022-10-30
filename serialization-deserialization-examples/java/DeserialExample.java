// Java code for serialization and deserialization
// of a Java object
import java.io.*;

public class DeserialExample {

	public static void main(String[] args)
	{
		String filename = null;
        if (args.length == 1) {
			filename = args[0]; 
        }
        else {
            System.out.println("Usage <java DeserialExample serial.ser>");
            System.exit(1);
        }
		DummyObject1 object = null;

		// Deserialization
		try {

			// Reading the object from a file
			FileInputStream file = new FileInputStream(args[0]);
			ObjectInputStream in = new ObjectInputStream(file);

			// Method for deserialization of object
			object = (DummyObject1)in.readObject();

			in.close();
			file.close();
			System.out.println("Object has been deserialized\n" + "Data after Deserialization.");
			DummyObject1.printdata(object);

			// System.out.println("z = " + object1.z);
		}

		catch (IOException ex) {
			System.out.println("IOException is caught");
		}

		catch (ClassNotFoundException ex) {
			System.out.println("ClassNotFoundException" +
								" is caught");
		}
	}
}