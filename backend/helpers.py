from os import environ
from dotenv import load_dotenv
from datetime import datetime
from sql import get_db
import math
import time

load_dotenv()


def timestamp_now():
    """
    Get the current timestamp in seconds.

    Returns:
        int: The current timestamp.
    """
    return math.floor(time.time())


mb = 1 * 10 ** 6
update_interval = int(environ["UPDATE_INTERVAL"])  # seconds
max_graph_size = int(environ["MAX_GRAPH_SIZE"])
traffic_data = {"upload": 0, "download": 0, "last_timestamp": timestamp_now()}
threats_data = {"alerts": 0, "last_timestamp": timestamp_now()}
concern_rating = float(environ["CONCERN_RATING"])
concern_rating_severe = float(environ["CONCERN_RATING_SEVERE"])
initial_year = int(environ["INITIAL_YEAR"])
initial_quarter = int(environ["INITIAL_QUARTER"])
technical_risk_score_growth_rate = int(environ["TECHNICAL_RISK_SCORE_GROWTH_RATE"])
alert_limit = int(environ["ALERT_LIMIT"])

alert_text = {
    "good_employee_percent": ("Employee Cybersecurity Habits", "Only {0}% of employees practice good cybersecurity habits.", False),
    "areas_of_concern": ("Areas of Concern Found", "{0} areas of concern were found from uploaded social data.", True),
    "employee_risk": ("{0} Employees Found", "{0} employees considered {1} were found.", False),
    "technical_risk_score": ("Scan Complete", "A scan with risk score of {0} was completed.", False),
    "open_port": ("Technical Risk Found", "Port {0} is open.", False)
}


def format_alert(title, body, time, is_severe):
    """
    Format an alert.

    Args:
        title (str): The title of the alert.
        body (str): The body of the alert.
        time (int): The timestamp of the alert.
        is_severe (bool): Indicates if the alert is severe.

    Returns:
        dict: The formatted alert.
    """
    return {
        "title": title,
        "body": body,
        "time": time,
        "isSevere": is_severe
    }


def format_user(name, time, ip, upload, download, upload_total, download_total):
    """
    Format user data.

    Args:
        name (str): The name of the user.
        time (int): The timestamp of the user data.
        ip (str): The IP address of the user.
        upload (float): The upload speed of the user.
        download (float): The download speed of the user.
        upload_total (float): The total upload data of the user.
        download_total (float): The total download data of the user.

    Returns:
        dict: The formatted user data.
    """
    return {
        "name": name,
        "time": format_time(time),
        "ip": ip,
        "upload": f"{upload} M/s",
        "download": f"{download} M/s",
        "upload_total": f"{math.floor(upload_total / mb)} M",
        "download_total": f"{math.floor(download_total / mb)} M"
    }


def formatted_alert(alert_name, title_format=None, body_format=None, severe_override=None):
    """
    Format an alert based on its name and optional formats.

    Args:
        alert_name (str): The name of the alert.
        title_format (tuple or str, optional): The format for the alert title. Defaults to None.
        body_format (tuple or str, optional): The format for the alert body. Defaults to None.
        severe_override (bool, optional): Override the severity of the alert. Defaults to None.

    Returns:
        None
    """
    if alert_name not in alert_text:
        return
    title, body, severe = alert_text[alert_name]

    if title_format is not None:
        if isinstance(title_format, tuple):
            title = title.format(*title_format)
        else:
            title = title.format(title_format)

    if body_format is not None:
        if isinstance(body_format, tuple):
            body = body.format(*body_format)
        else:
            body = body.format(body_format)

    if severe_override is not None:
        severe = severe_override

    add_alert(title, body, severe)


def add_alert(title, body, severe):
    """
    Add an alert to the database.

    Args:
        title (str): The title of the alert.
        body (str): The body of the alert.
        severe (bool): Indicates if the alert is severe.

    Returns:
        None
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO alerts (Title, Body, Timestamp, Severe) VALUES (%s, %s, %s, %s);", (title, body, timestamp_now(), severe))

    time_now = timestamp_now()

    if time_now - threats_data["last_timestamp"] >= update_interval:
        cur.execute("INSERT INTO threats (Value) VALUES (%s);", (threats_data["alerts"],))

        threats_data["alerts"] = 0
        threats_data["last_timestamp"] = timestamp_now()

    threats_data["alerts"] += 1

    db.commit()
    db.close()


def format_time(timestamp):
    """
    Format a timestamp into a human-readable string.

    Args:
        timestamp (int or str): The timestamp to format.

    Returns:
        str: The formatted timestamp.
    """
    try:
        timestamp = int(timestamp)
    except ValueError:
        pass

    if type(timestamp) != int:
        return timestamp

    now = datetime.now()
    if type(timestamp) is int:
        diff = now - datetime.fromtimestamp(timestamp)
    elif isinstance(time, datetime):
        diff = now - timestamp
    else:
        diff = 0
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 5:
            return "now"
        if second_diff < 60:
            return str(second_diff) + "s"
        if second_diff < 3600:
            return str(second_diff // 60) + "m"
        if second_diff < 86400:
            return str(second_diff // 3600) + "h"
    if day_diff < 7:
        return str(day_diff) + "D"
    if day_diff < 31:
        return str(day_diff // 7) + "W"
    if day_diff < 365:
        return str(day_diff // 30) + "M"
    return str(day_diff // 365) + "Y"


def network_traffic_update(upload, download):
    """
    Adds new total upload/download data to the network traffic graph and updates every 1 minute.

    Args:
        upload (float): The upload data to add.
        download (float): The download data to add.

    Returns:
        None
    """
    traffic_data["upload"] += upload
    traffic_data["download"] += download
    time_now = timestamp_now()

    if time_now - traffic_data["last_timestamp"] >= update_interval:
        db = get_db()
        cur = db.cursor()
        for t in [(traffic_data["upload"], True),
                  (traffic_data["download"], False)]:
            cur.execute("INSERT INTO traffic (Value, IsUpload) VALUES (%s, %s);", t)

        traffic_data["upload"] = 0
        traffic_data["download"] = 0
        traffic_data["last_timestamp"] = time_now

        cur.execute("SELECT Name, LastTime FROM users;")
        for user in cur:
            name, last_time = user
            if time_now - last_time >= update_interval:
                cur.execute("DELETE FROM users WHERE Name = %s;", (name,))

        db.commit()
        db.close()
