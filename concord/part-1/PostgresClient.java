import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import static java.util.Arrays.asList;
import java.util.ArrayList;
import java.util.List;
public class PostgresClient {
  private String ip = null;
  private String port = null;
  private String usr = null;
  private String pwd = null;
  private String url = null;
  Connection c = null;
  public PostgresClient(String ip, String port, String usr, String pwd) {
    this.ip = ip;
    this.port = port;
    this.usr = usr;
    this.pwd = pwd;
    this.url = String.format("jdbc:postgresql://%s:%s/postgres", ip, port);
    try {
    Class.forName("org.postgresql.Driver");
    c = DriverManager.getConnection(this.url, this.usr, this.pwd);
    }catch(Exception e) {
      log("(-) Failed to connect to: " + this.url);
      System.err.println(e.getClass().getName()+": "+e.getMessage());
      System.exit(0);
    }
    log("(+) Connection Success!");

  }
  private void log(String message) {
    System.out.println(String.format("%s", message));
  }
  public void update(String table, List<String> columns, List<String> columnsConditions, List<String> columnsConditionsValues, String ... values) {
    ArrayList<String> queries = new ArrayList<String>();
    for (int i = 0; i < columns.size(); ++i) {
        String sql = String.format("UPDATE %s SET %s = '%s' where %s = '%s'", table,columns.get(i), values[i], columnsConditions.get(i), columnsConditionsValues.get(i));
        queries.add(sql);
        log("(+) " + sql);
    }
    try {
      for (int i = 0; i < queries.size(); ++i) {
         Statement stmt = this.c.createStatement();
         stmt.executeUpdate(queries.get(i));
         stmt.close();
      }
    } catch(Exception e) {
         log("(-) Failure in Update");
         log("(-) " + e.getClass().getName()+": "+e.getMessage());
         System.exit(0);        
    }
  }
  public void getTables(Connection c) {
    log("(+) Attempting to retrieve tables");
    try {
       Statement stmt = null;
       String sql = "SELECT * FROM information_schema.tables";
       stmt = this.c.createStatement();
       ResultSet rs = stmt.executeQuery(sql);
       log("(+) ");
       while ( rs.next() ) {
          log(String.format("(+) Table Name: %s",rs.getString("table_name")));
       }
       rs.close();
       stmt.close();
    } catch (Exception e) {
       log("(-) Failure in getTables");
       log("(-) "+ e.getClass().getName()+": "+e.getMessage());
       System.exit(0);
    }
  }
  public void getPermissions(String table) {
     log(String.format("(+) Attempting to retrieve permissions for table: %s", table));
     try {
        Statement stmt = null;
        String sql = String.format("SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name='%s'", table);
        stmt = this.c.createStatement();
        ResultSet rs = stmt.executeQuery(sql);
        log("(+) Grantee Privilege Type");
        while ( rs.next() ) {
           System.out.println(String.format("(+) %s %s",rs.getString("grantee"),rs.getString("privilege_type")));
        }
        rs.close();
        stmt.close();
     } catch(Exception e) {
        log("(-) Failure in getPermissions");
        log(e.getClass().getName()+": "+e.getMessage());
        System.exit(0);
     }
  }
  public void getColumns(String table) {
    System.out.println(String.format("(+) Attempting to retrieve column names from table: %s", table));
    try {
        Statement stmt = null;
        String sql = String.format("SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '%s'", table);
        stmt = this.c.createStatement();
        ResultSet rs = stmt.executeQuery(sql);
        while ( rs.next() ) {
          log(String.format("(+) Column Name: %s | Datatype: %s",rs.getString("column_name"), rs.getString("data_type")));
        }
        rs.close();
        stmt.close();
    } catch(Exception e) {
        log("(-) Failure in getColumns");
        log(e.getClass().getName()+": "+e.getMessage());
        System.exit(0);
    }
  }
  public static void main(String args[]) {
    PostgresClient pgc = null;
    String db = "";
    String port = "";
    try {
        if(args.length != 4) {
          throw new Exception("(-) Usage: java PostgresClient ip port usr pwd");
        }
        else {
          pgc = new PostgresClient(args[0], args[1], args[2], args[3]);
          pgc.update( "api_keys", asList("api_key"), asList("user_id"), asList("d4f123c1-f8d4-40b2-8a12-b8947b9ce2d8"), "api key value");
        }
        
    } catch (Exception e) {
        System.err.println(e.getClass().getName()+": "+e.getMessage());
        System.exit(0);
    }
  }
}
