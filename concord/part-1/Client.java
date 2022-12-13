import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class Client {
   public static void getTables(Connection c) {
      System.out.println("(+) Attempting to retrieve tables");
      try {
         Statement stmt = null;
         String sql = "SELECT * FROM information_schema.tables";
         stmt = c.createStatement();
         ResultSet rs = stmt.executeQuery(sql);
         while ( rs.next() ) {
            System.out.println(String.format("(+) Table Name: %s",rs.getString("table_name")));
         }
         rs.close();
         stmt.close();
      } catch (Exception e) {
         System.err.println("(-) Failure in getTables");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }
   public static void main(String args[]) {
      Connection c = null;
      String db = "";
      String port = "";
      try {
         if(args.length != 2) {
            System.exit(0);
         }
         else {
            db = args[0];
            port = args[1];
         }
         Class.forName("org.postgresql.Driver");
         String url = String.format("jdbc:postgresql://%s:%s/postgres", db, port);
         c = DriverManager.getConnection(url, "postgres", "quake1quake2quake3arena");
         getTables(c);
         c.close();
      } catch (Exception e) {
         e.printStackTrace();
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }
}