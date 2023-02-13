import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Base64;
import java.util.Random;


public class PasswordCracker
{
  public static final int password_length = 16;
  public static final String CHARSET = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".toUpperCase() + "1234567890" + "!@#$%^&*()";
  public static String generatePassword(int length, long seed) {
    Random random = new Random(seed);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < length; i++) {
      sb.append(CHARSET.charAt(random.nextInt(CHARSET.length())));
    }
    return sb.toString();
  }

  
  public static String hashPassword(String pass) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA1");
    return Base64.getEncoder().encodeToString(md.digest(pass.getBytes("UTF-8")));
  }
  
  public static boolean comparePasswords(String pass, String hash) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA1");
    byte[] hashedPass = md.digest(pass.getBytes("UTF-8"));
    byte[] decodedHash = Base64.getDecoder().decode(hash);
    return Arrays.equals(hashedPass, decodedHash);
  }
  public static void main(String args[]) {
    long start = 0;
    long stop = 0;
    String hash = "";
    if (args.length != 3) {
    	System.out.println("Usage: java PasswordCracker <start> <stop> <hash>");
    	System.out.println("Example java PasswordCracker 1582038122371 1582038122769 <sha1sum>");
    	System.exit(-1);
    }
    int length = password_length;
    start = Long.parseLong(args[0]);
    stop = Long.parseLong(args[1]);
    hash = args[2];
    for (long l = start; l <= stop; l++) {
      try {
     // compare to see if like password pulled from db  
     String plaintext = generatePassword(length, l);
     System.out.println(plaintext);
     if(comparePasswords(hashPassword(plaintext), hash)) {
      System.out.println("Found Password: " + plaintext);
    }
      }
      catch(Exception e) {

      }

  }
}
}