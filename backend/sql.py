from os import environ
from dotenv import load_dotenv
import mysql.connector 


load_dotenv()


def get_db():
    """
    Connects to the MySQL database and returns the connection object.

    Returns:
        mysql.connector.connection.MySQLConnection: The connection object to the MySQL database.
    """
    return mysql.connector.connect(
        host="db",
        user="root",
        password=environ["DB_PASSWORD"],
        database="deco",
    )


def setup_db():
    """
    Sets up the database by creating necessary tables if they don't exist.

    This function creates the following tables:
    - alerts
    - users
    - traffic
    - threats
    - social_overview
    - employee_risk_level
    - vulnerability_overall
    - areasofconcerns
    - departmentscores
    - scores_column
    - scores_row
    - scores_value
    - historical_risk
    - technical_risks_issues
    - historical_technical_risk
    - vulnerabilities
    - nmap_scans

    """
    db = get_db()
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS alerts (ID int NOT NULL AUTO_INCREMENT, Title varchar(255) NOT NULL, Body varchar(255) NOT NULL, Timestamp int NOT NULL, Severe BOOL NOT NULL, PRIMARY KEY (ID));")
    cur.execute("CREATE TABLE IF NOT EXISTS users (ID int NOT NULL AUTO_INCREMENT, Name varchar(255) NOT NULL, Time int NOT NULL, LastTime int NOT NULL, IP varchar(255) NOT NULL, Upload_Per_Second int NOT NULL, Upload_Total double NOT NULL, Download_Per_Second int NOT NULL, Download_Total double NOT NULL, PRIMARY KEY (ID));")
    cur.execute("CREATE TABLE IF NOT EXISTS traffic (Value bigint NOT NULL, IsUpload bool NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS threats (ID int NOT NULL AUTO_INCREMENT, Value int NOT NULL, PRIMARY KEY (ID));")

    # These tables should only ever have one row
    cur.execute("CREATE TABLE IF NOT EXISTS social_overview (good_employee_percent int NOT NULL, best_dept varchar(255) NOT NULL, worst_dept varchar(255) NOT NULL, overall_percent int NOT NULL, averageKnowledge int NOT NULL, averageAttitude int NOT NULL, averageBehaviour int NOT NULL, time int NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS employee_risk_level (VeryLow int NOT NULL, Low int NOT NULL, Moderate int NOT NULL, High int NOT NULL, VeryHigh int NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS vulnerability_overall (Score int NOT NULL, Criticality int NOT NULL);")

    cur.execute("CREATE TABLE IF NOT EXISTS areasofconcerns (Name varchar(255) NOT NULL, Severity int NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS departmentscores (Name varchar(255) NOT NULL, Score int NOT NULL);")

    cur.execute("CREATE TABLE IF NOT EXISTS scores_column (CID int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (CID));")
    cur.execute("CREATE TABLE IF NOT EXISTS scores_row (RID int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (RID));")
    cur.execute("CREATE TABLE IF NOT EXISTS scores_value (CID int NOT NULL, RID int NOT NULL, Value int NOT NULL);")

    cur.execute("CREATE TABLE IF NOT EXISTS historical_risk (Year int NOT NULL, Quarter int NOT NULL, Percent int NOT NULL);")

    cur.execute("CREATE TABLE IF NOT EXISTS technical_risks_issues (Name varchar(255) NOT NULL, Status int NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS historical_technical_risk (Year int NOT NULL, Quarter int NOT NULL, Percent int NOT NULL);")
    cur.execute("CREATE TABLE IF NOT EXISTS vulnerabilities (Name varchar(255) NOT NULL, Score int NOT NULL);")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS nmap_scans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            target VARCHAR(255) NOT NULL,
            scan_type VARCHAR(20) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            results TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()
