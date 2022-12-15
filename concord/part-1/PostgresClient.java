import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
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
        }
        
    } catch (Exception e) {
        System.err.println(e.getClass().getName()+": "+e.getMessage());
        System.exit(0);
    }
  }
}
