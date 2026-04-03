"""
This file contains the main Flask application for the Digital Defenders backend.
It includes routes for network scanning, Nmap scan execution, retrieving recent scan results,
and API endpoints for index.html and social-risk.html.

The main functionalities of this application include:
- Running Nmap scans on specified targets with different scan types and exclusion options
- Storing scan results in a database
- Retrieving recent scan results
- Generating API data for index.html and social-risk.html

Please note that this code assumes the existence of the following modules and functions:
- Flask: A micro web framework for Python
- render_template: A function for rendering HTML templates
- request: A module for handling HTTP requests
- redirect: A function for redirecting to a different URL
- jsonify: A function for creating JSON responses
- load_dotenv: A function for loading environment variables from a .env file
- get_db: A function for getting a database connection
- setup_db: A function for setting up the database
- main_schedule: A function for running scheduled tasks in the background
- Thread: A class for creating and managing threads
- ProxyFix: A middleware for fixing proxy headers
- requests: A module for making HTTP requests
- io: A module for working with streams
- json: A module for working with JSON data
- subprocess: A module for spawning new processes
- helpers: A module containing helper functions
- csvRead: A module for reading CSV files
- xmlRead: A module for reading XML files
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from sql import get_db, setup_db
from werkzeug.middleware.proxy_fix import ProxyFix
import io
import json
import subprocess
import helpers
import csvRead
import xmlRead


load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

setup_db()


# Network scan route
@app.route("/network")
def network():
    """
    This function handles the '/network' route and retrieves the 5 most recent nmap scans from the database.
    
    Returns:
        The rendered 'network.html' template with the recent scans passed as a parameter.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM nmap_scans ORDER BY timestamp DESC LIMIT 5")
    recent_scans = cur.fetchall()
    return render_template("network.html", recent_scans=recent_scans)

# Nmap scan execution
@app.route("/runnmapscan", methods=["POST"])
def run_nmap_scan():
    """
    Run an Nmap scan based on the provided parameters.

    Returns:
        A JSON response containing the scan results or an error message.
    """
    try:
        data = json.loads(request.data)
        target = data['target']
        scan_type = data['scan_type']
        exclude_zones = data.get('exclude_zones', 'n')
        additional_excludes = data.get('additional_excludes', '')

        # Construct the Nmap command securely using a list
        scan_options = []
        if scan_type == "Light":
            scan_options = ["-oX", "-", "-T4", "-sS", "-sV", "-O"]
        elif scan_type == "Moderate":
            scan_options = ["-oX", "-", "-T4", "-sS", "-sV", "-O", "-p-", "-sU"]
        elif scan_type == "Aggressive":
            scan_options = ["-oX", "-", "-T4", "-sS", "-sV", "-O", "-p-", "-sU", "-sC", "--traceroute"]

        # Exclusion logic
        exclude_hosts = []
        if exclude_zones == "y":
            exclude_hosts = ["--exclude", "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"]
        if additional_excludes:
            exclude_hosts.append(additional_excludes)

        # Run the Nmap command
        nmap_command = ["nmap"] + scan_options + exclude_hosts + [target]
        print(f"Running Nmap command: {' '.join(nmap_command)}")  # Debug log

        result = subprocess.run(nmap_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Nmap scan failed: {result.stderr}")
            return jsonify({"success": False, "message": "Nmap scan failed", "error": result.stderr}), 500

        scan_text = result.stdout

        # Log the scan result for debugging
        print(f"Scan completed successfully. Output: {scan_text}")


        # Store results in database
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO nmap_scans (target, scan_type, results) VALUES (%s, %s, %s)",
            (target, scan_type, scan_text)
        )

        port_info = xmlRead.get_results_from_string(scan_text, helpers.technical_risk_score_growth_rate)

        cur.execute("DELETE FROM vulnerability_overall;")
        v = (port_info["risk_score"], port_info["criticality"])
        cur.execute("INSERT INTO vulnerability_overall (Score, Criticality) VALUES (%s, %s);", v)

        helpers.formatted_alert("technical_risk_score", body_format=port_info["risk_score"], severe_override=port_info["criticality"] != 2)

        cur.execute("DELETE FROM technical_risks_issues;")
        for port_num in port_info["open_ports"]:
            v = (f"Port {port_num} is open.", 1)
            cur.execute("INSERT INTO technical_risks_issues (Name, Status) VALUES (%s, %s);", v)

            helpers.formatted_alert("open_port", body_format=port_num)

        last_year = helpers.initial_year
        last_quarter = helpers.initial_quarter
        cur.execute("SELECT Year, Quarter FROM historical_technical_risk;")
        for r in cur:
            last_year, last_quarter = r[0], r[1]
        current_year = last_year + 1 if last_quarter == 4 else last_year
        current_quarter = 1 if last_quarter == 4 else last_quarter + 1
        cur.execute("INSERT INTO historical_technical_risk (Year, Quarter, Percent) VALUES (%s, %s, %s);",
                    (current_year, current_quarter, port_info["risk_score"]))

        # This is not a good way of doing this
        cur.execute("DELETE FROM vulnerabilities;")
        v = (f"Open Ports", 1)
        cur.execute("INSERT INTO vulnerabilities (Name, Score) VALUES (%s, %s);", v)

        db.commit()

        # Return results to be displayed on the page
        return jsonify({"success": True, "results": scan_text})

    except Exception as e:
        print(f"Error running Nmap scan: {str(e)}")
        return jsonify({"success": False, "message": "Error running scan", "error": str(e)}), 500

# Route to get recent scan results
@app.route("/get_recent_scans")
def get_recent_scans():
    """
    Retrieves the most recent scans from the database.

    Returns:
        A JSON response containing the most recent scans.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, target, scan_type, timestamp FROM nmap_scans ORDER BY timestamp DESC LIMIT 5")
    scans = cur.fetchall()
    return jsonify({
        "scans": [
            {
                "id": scan[0],
                "target": scan[1],
                "scan_type": scan[2],
                "timestamp": scan[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for scan in scans
        ]
    })

# Route to get specific scan results by scan_id
@app.route("/get_scan_results/<int:scan_id>")
def get_scan_results(scan_id):
    """
    Retrieves the scan results for a given scan ID from the database.

    Args:
        scan_id (int): The ID of the scan.

    Returns:
        A JSON response containing the scan results if the scan is found, 
        otherwise a JSON response indicating that the scan was not found.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT results FROM nmap_scans WHERE id = %s", (scan_id,))
    result = cur.fetchone()
    if result:
        return jsonify({"success": True, "results": result[0]})
    else:
        return jsonify({"success": False, "message": "Scan not found"})

# API info for /index.html
@app.route("/index")
def index():
    """
    Retrieves data from the database and constructs a response object.

    Returns:
        dict: A dictionary containing various data retrieved from the database.
    """
    db = get_db()
    cur = db.cursor()

    max_graph_size = helpers.max_graph_size
    r = {}

    overview = {}

    users = []
    cur.execute("SELECT Name, Time, IP, Upload_Per_Second, Download_Per_Second, Upload_Total, Download_total FROM users;")
    for u in cur:
        users.append(helpers.format_user(u[0], u[1], u[2], u[3], u[4], u[5], u[6]))

    issues = []
    cur.execute("SELECT * FROM technical_risks_issues;")
    for i in cur:
        issues.append(i)

    overview["active_users"] = len(users)
    overview["open_ports"] = len(issues)

    overview["good_employee_percent"] = 100
    overview["overall_percent"] = 0
    cur.execute("SELECT * FROM social_overview;")
    for d in cur:
        overview["good_employee_percent"] = d[0]
        overview["overall_percent"] = d[3]

    alerts = []
    cur.execute("SELECT * FROM alerts ORDER BY Timestamp DESC LIMIT %s;", (helpers.alert_limit,))
    for d in cur:
        alerts.append(helpers.format_alert(d[1], d[2], helpers.format_time(d[3]), d[4]))

    traffic_up = []
    cur.execute("SELECT * FROM traffic WHERE IsUpload is true;")
    for u in cur:
        traffic_up.append(round(u[0] / helpers.mb))
    traffic_up = traffic_up[-max_graph_size:]  # Only get last 5 items (MAX_GRAPH_SIZE = 5)
    while len(traffic_up) < max_graph_size:
        traffic_up = [0] + traffic_up

    traffic_down = []
    cur.execute("SELECT * FROM traffic WHERE IsUpload is false;")
    for d in cur:
        traffic_down.append(round(d[0] / helpers.mb))
    traffic_down = traffic_down[-max_graph_size:]  # Only get last 5 items (MAX_GRAPH_SIZE = 5)
    while len(traffic_down) < max_graph_size:
        traffic_down = [0] + traffic_down


    threats = []
    cur.execute("SELECT Value FROM threats;")
    for d in cur:
        threats.append(d[0])
    threats = threats[-max_graph_size:]
    while len(threats) < max_graph_size:
        threats = [0] + threats

    r["overview"] = overview
    r["users"] = users
    r["alerts"] = alerts
    r["traffic_up"] = traffic_up
    r["traffic_down"] = traffic_down
    r["threats"] = threats

    db.commit()
    db.close()

    return r


# API info for /social-risk.html
@app.route("/social")
def social():
    """
    Retrieves social data from the database and returns it as a dictionary.

    Returns:
        dict: A dictionary containing social data including overview, areas of concern,
              department scores, employee risk level, scores, and historical data.
    """
    db = get_db()
    cur = db.cursor()
    r = {}

    overview = {
        "good_employee_percent": 100,
        "best_dept": "N/A",
        "worst_dept": "N/A",
        "overall_percent": 0
    }
    averageKnowledge, averageAttitude, averageBehaviour = 100, 100, 100
    cur.execute("SELECT * FROM social_overview;")  # Should only have 1 row
    for d in cur:
        overview = {
            "good_employee_percent": d[0],
            "best_dept": d[1],
            "worst_dept": d[2],
            "overall_percent": d[3],
            "time": d[7]
        }
        averageKnowledge, averageAttitude, averageBehaviour = d[4], d[5], d[6]
    percents_good = {"Knowledge": averageKnowledge, "Attitude": averageAttitude, "Behaviour": averageBehaviour}

    areas_of_concern = []
    cur.execute("SELECT * FROM areasofconcerns;")
    for a in cur:
        areas_of_concern.append({"name": a[0], "severity": a[1]})
    # 2 for severe, 1 for moderate, 0 for normal?

    departments = {}
    cur.execute("SELECT * FROM departmentscores;")
    for d in cur:
        departments[d[0]] = {"score": d[1]}
        departments[d[0]]["hazard"] = False if departments[d[0]]["score"] > 2 else True

    employee_risk_level = [0] * 5
    cur.execute("SELECT * FROM employee_risk_level;")
    for l in cur:
        employee_risk_level = list(l)

    scores = []
    columns = {}
    cur.execute("SELECT scores_column.Name, scores_row.Name, scores_value.Value FROM scores_value JOIN scores_column ON scores_value.CID = scores_column.CID JOIN scores_row ON scores_value.RID = scores_row.RID;")
    for s in cur:
        column = s[0]
        row = s[1]
        value = s[2]
        if column not in columns:
            columns[column] = []
        columns[column].append({"name": row, "value": value})
    for col in columns:
        all_scores = []
        for row in columns[col]:
            all_scores.append(row["value"])
        scores.append({"name": col, "scores": columns[col],
                       "percent_good": percents_good[col]})

    historical = []
    cur.execute("SELECT * FROM historical_risk;")
    for h in cur:
        historical.append({"label": f"{h[0]}'Q{h[1]}", "score": h[2]})

    r["overview"] = overview
    r["areas_of_concern"] = areas_of_concern
    r["departments"] = departments
    r["employee_risk_level"] = employee_risk_level
    r["scores"] = scores
    r["historical"] = historical
    return r


# API info for /technical-risk.html
@app.route("/technical")
def technical():
    """
    Retrieves technical information from the database and returns it as a JSON response.

    Returns:
        dict: A dictionary containing technical information, including score, criticality, issues, historical data, and vulnerabilities.
    """
    db = get_db()
    cur = db.cursor()
    r = {}

    r["score"] = 0
    r["criticality"] = 0
    cur.execute("SELECT * FROM vulnerability_overall;")
    for overall in cur:
        r["score"] = overall[0]
        r["criticality"] = overall[1]  # 0 = "LOW", 1 = "MEDIUM", 2 = "HIGH"

    r["issues"] = []
    cur.execute("SELECT * FROM technical_risks_issues")
    for issue in cur:
        r["issues"].append({"name": issue[0], "status": issue[1]})  # Status: 0 = "low?", 1 = "moderate", 2 = "severe"

    r["historical"] = []
    cur.execute("SELECT * FROM historical_technical_risk;")
    for h in cur:
        r["historical"].append({"label": f"{h[0]}'Q{h[1]}", "score": h[2]})

    r["vulnerabilities"] = []
    vuln_data = []
    cur.execute("SELECT * FROM vulnerabilities;")
    for vuln in cur:
        vuln_data.append(vuln)

    vuln_total = 0
    for vuln in vuln_data:
        vuln_total += vuln[1]

    percent_total = 0
    for vuln in vuln_data:
        percent = round((vuln[1] / vuln_total) * 100)
        percent_total += percent
        r["vulnerabilities"].append({"name": vuln[0], "percent": percent})

    while percent_total < 100 and len(r["vulnerabilities"]) > 0:  # Should only run once
        r["vulnerabilities"][0]["percent"] += 1
        percent_total += 1

    return r


# Only used in monitor.py
@app.route("/userupdate", methods=["POST"])
def user_update():
    """
    Update user information in the database.

    This function takes in user information from the request JSON and updates the corresponding user record in the database.
    The function performs the following steps:
    1. Checks if all the required fields (name, ip, up_total, down_total, up_per_second, down_per_second) are present in the user information.
    2. Retrieves the current upload and download totals for the user from the database.
    3. Updates the upload and download totals with the new values provided by the user.
    4. Calls a helper function to update the network traffic information.
    5. Updates the user record in the database with the new information.
    6. Commits the changes to the database.
    
    Returns:
    - If the user record is successfully updated, returns the string "Updated".
    - If any required field is missing in the user information, returns an error message along with the HTTP status code 400.
    """
    user = request.json

    fields = ["name", "ip", "up_total", "down_total", "up_per_second", "down_per_second"]
    for f in fields:
        if f not in user:
            return f"Couldn't find {f}.", 400

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT Upload_Total, Download_Total FROM users WHERE Name = %s;", (user["name"],))
    found = 0
    results = []
    for r in cur:
        results.append(r)
        found += 1

    if found:
        old_up_total, old_down_total = results[0][0], results[0][1]
        up_total = old_up_total + user["up_total"]
        down_total = old_down_total + user["down_total"]
        helpers.network_traffic_update(user["up_total"], user["down_total"])
        values = (helpers.timestamp_now(), user["ip"], user["up_per_second"], up_total, user["down_per_second"], down_total, user["name"])
        cur.execute("UPDATE users SET LastTime = %s, IP = %s, Upload_Per_Second = %s, Upload_Total = %s, Download_Per_Second = %s, Download_Total = %s WHERE Name = %s;", values)
    else:
        timestamp = helpers.timestamp_now()
        values = (user["name"], timestamp, timestamp, user["ip"], user["up_per_second"], user["up_total"], user["down_per_second"], user["down_total"])
        cur.execute("INSERT INTO users (Name, Time, LastTime, IP, Upload_Per_Second, Upload_Total, Download_Per_Second, Download_Total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", values)
    db.commit()
    db.close()
    return "Updated"


@app.route("/socialupdate", methods=["POST"])
def upload_social_risks_data():
    """
    Uploads social risks data and updates the database with the results.

    Returns:
        dict: The result of the data upload and database update.
    """
    if request.data is None or len(request.data) == 0:
        return "No upload", 400
    csv_stream = io.StringIO(request.data.decode())
    result = csvRead.updateSurveyResults(csv_stream, helpers.concern_rating, helpers.concern_rating_severe)

    db = get_db()
    cur = db.cursor()

    # Overview
    social_overview = (result["good_employee_percent"], result["best_dept"], result["worst_dept"], result["risk_percent"], result["averageKnowledge"], result["averageAttitude"], result["averageBehaviour"], helpers.timestamp_now())
    cur.execute("DELETE FROM social_overview;")
    cur.execute("INSERT INTO social_overview (good_employee_percent, best_dept, worst_dept, overall_percent, averageKnowledge, averageAttitude, averageBehaviour, time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", social_overview)

    if result["good_employee_percent"] <= 50:
        severe_override = True if result["good_employee_percent"] <= 25 else False
        helpers.formatted_alert("good_employee_percent", body_format=result["good_employee_percent"], severe_override=severe_override)

    # Areas of Concern
    cur.execute("DELETE FROM areasofconcerns;")
    for area in result["areas_of_concern"]:
        new_area = (area["name"], 2 if area["severe"] else 1)
        cur.execute("INSERT INTO areasofconcerns (Name, Severity) VALUES (%s, %s)", new_area)

    if len(result["areas_of_concern"]) > 2:
        helpers.formatted_alert("areas_of_concern", body_format=len(result["areas_of_concern"]))

    # Employee Risk Levels
    cur.execute("DELETE FROM employee_risk_level;")
    employee_risk_level = tuple(result["employee_risk_level"])
    cur.execute("INSERT INTO employee_risk_level (VeryLow, Low, Moderate, High, VeryHigh) VALUES (%s, %s, %s, %s, %s);", employee_risk_level)

    if employee_risk_level[3] > 2:  # High risk employees
        helpers.formatted_alert("employee_risk", title_format="High Risk", body_format=(employee_risk_level[3], "high risk"))
    if employee_risk_level[4] > 2:  # Very high risk employees
        helpers.formatted_alert("employee_risk", title_format="Very High Risk", body_format=(employee_risk_level[4], "very high risk"), severe_override=True)

    # Scores
    cur.execute("DELETE FROM scores_column;")
    cur.execute("DELETE FROM scores_row;")
    cur.execute("DELETE FROM scores_value;")

    column = result["column"]
    row = result["row"]
    for i, c in enumerate(column):
        cur.execute("INSERT INTO scores_column (CID, Name) VALUES (%s, %s);", (i, c))
    for j, r in enumerate(row):
        cur.execute("INSERT INTO scores_row (RID, Name) VALUES (%s, %s);", (j, r))
    for i, c in enumerate(column):
        for j, r in enumerate(row):
            new_score = (i, j, result["overall"][c][r])
            cur.execute("INSERT INTO scores_value (CID, RID, Value) VALUES (%s, %s, %s);", new_score)

    # Historical Risk
    last_year = helpers.initial_year
    last_quarter = helpers.initial_quarter
    cur.execute("SELECT Year, Quarter FROM historical_risk;")
    for r in cur:
        last_year, last_quarter = r[0], r[1]
    current_year = last_year + 1 if last_quarter == 4 else last_year
    current_quarter = 1 if last_quarter == 4 else last_quarter + 1
    cur.execute("INSERT INTO historical_risk (Year, Quarter, Percent) VALUES (%s, %s, %s);", (current_year, current_quarter, result["risk_percent"]))

    cur.execute("DELETE FROM departmentscores;")
    for dept in result["departments"]:
        new_deptscore = (dept, result["departments"][dept])
        cur.execute("INSERT INTO departmentscores (Name, Score) VALUES (%s, %s);", new_deptscore)

    db.commit()
    db.close()

    return result
