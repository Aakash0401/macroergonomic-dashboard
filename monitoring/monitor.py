import os, time, requests, math

timeout = 5
MB = 1 * 10 ** 6
username = os.environ.get("USERNAME")
if username is None:
    username = os.environ.get("USER")
if username is None:
    username = "User"
endpoint = "http://localhost:8000/api/userupdate"  # default
try:
    with open("config.txt") as f:
        endpoint = f.read()
except:
    pass

own_ip = requests.get("http://ifconfig.me/ip").text


def get_total():
    time_now = time.time()

    if os.name == "nt":
        netstat = os.popen("netstat -e").read()

        values = []
        for line in netstat.split("\n"):
            if line.startswith("Bytes"):
                for v in line.split(" "):
                    if not (v == "" or v == "Bytes"):
                        values.append(int(v))

        if len(values) != 2:
            print("Cannot get upload/download values.")
            exit(1)

        download, upload = values
    else:
        netstat = os.popen("netstat -s").read()

        download, upload = None, None
        for line in netstat.split("\n"):
            line = line.strip()
            if line.startswith("InOctets"):
                download = int(line.split(" ")[1])
            if line.startswith("OutOctets"):
                upload = int(line.split(" ")[1])

        if download is None or upload is None:
            print("Cannot get upload/download values.")
            exit(1)

    return time_now, download, upload


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

        json = {
            "name": username,
            "ip": own_ip,
            "up_total": upload_diff,
            "down_total": download_diff,
            "up_per_second": upload_per_second,
            "down_per_second": download_per_second
        }

        print(json)
        sent = False
        while not sent:
            try:
                r = requests.post(endpoint, json=json)
                if r.status_code == 200:
                    sent = True
                if r.status_code != 200:
                    print(f"Failed to send data with status {r.status_code}. Retrying in {timeout} seconds. Response:\n{r.text}")
                    time.sleep(timeout)
            except requests.exceptions.ConnectionError:
                print(f"Failed to send data due to connection error. Retrying in {timeout} seconds.")
                time.sleep(timeout)


if __name__ == "__main__":
    main()
