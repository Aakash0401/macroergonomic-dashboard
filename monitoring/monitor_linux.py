import os, time, requests, math, re

timeout = 5
MB = 1 * 10 ** 6
username = os.environ.get("USER")  # use USER in Linux
endpoint = "http://localhost:8000/api/userupdate"  # default
try:
    with open("config.txt") as f:
        endpoint = f.read().strip()
except:
    pass


# Function to get the public IP address
def get_public_ip():
    try:
        return requests.get("http://ifconfig.me/ip").text.strip()
    except requests.exceptions.RequestException:
        print("Failed to get public IP address.")
        return None

public_ip = get_public_ip()

# Function to detect the active network interface
def get_interface_name():
    with open("/proc/net/dev") as f:
        net_dev = f.readlines()

    interfaces = []
    for line in net_dev:
        match = re.search(r'(\w+):', line)
        if match:
            interfaces.append(match.group(1))

    # Filter out lo (loopback) and any other inactive interfaces
    active_interface = None
    for interface in interfaces:
        if interface != "lo":  # ignoring loopback interface
            active_interface = interface
            break

    if not active_interface:
        print("No active network interface found.")
        exit(1)

    return active_interface


def get_total():
    time_now = time.time()

    active_interface = get_interface_name()
    try:
        with open("/proc/net/dev") as f:
            net_dev = f.readlines()

        values = []
        for line in net_dev:
            if active_interface in line:
                parts = line.split()
                download = int(parts[1])  # received bytes
                upload = int(parts[9])  # transmitted bytes
                values = [download, upload]
                break

        if len(values) != 2:
            print("Cannot get upload/download values.")
            exit(1)

        download, upload = values
        return time_now, download, upload
    except FileNotFoundError:
        print("Network device information not found. Is this Linux?")
        exit(1)


def main():
    download_per_second, upload_per_second = 0, 0
    time_last, download_last, upload_last = get_total()
    while True:
        time.sleep(timeout)
        time_new, download_new, upload_new = get_total()

        download_diff = download_new - download_last
        upload_diff = upload_new - upload_last
        time_diff = time_new - time_last

        if download_diff > 0 and upload_diff > 0 and time_diff > 0:
            download_per_second = math.floor(download_diff / time_diff) / MB
            upload_per_second = math.floor(upload_diff / time_diff) / MB

        time_last, download_last, upload_last = time_new, download_new, upload_new

        json_data = {
            "name": username,
            "up_total": upload_diff,
            "ip": public_ip,
            "down_total": download_diff,
            "up_per_second": upload_per_second,
            "down_per_second": download_per_second
        }

        print(json_data)
        sent = False
        while not sent:
            try:
                r = requests.post(endpoint, json=json_data)
                if r.status_code == 200:
                    sent = True
                else:
                    print(f"Failed to send data with status {r.status_code}. Retrying in {timeout} seconds. Response:\n{r.text}")
                    time.sleep(timeout)
            except requests.exceptions.ConnectionError:
                print(f"Failed to send data due to connection error. Retrying in {timeout} seconds.")
                time.sleep(timeout)


if __name__ == "__main__":
    main()