import java.io.*;

public class DummyObject1 implements Serializable {
	private static final long serialversionUID = 129348938L;
	public int a;
	public	int b;
	public	String name;
	public	int age;

	// Default constructor
	public DummyObject1(String name, int age, int a, int b)
	{
		this.name = name;
		this.age = age;
		this.a = a;
		this.b = b;
	}
	public static void printdata(DummyObject1 object1)
	{
		System.out.println("name = " + object1.name);
		System.out.println("age = " + object1.age);
		System.out.println("a = " + object1.a);
		System.out.println("b = " + object1.b);
	}

}