# DECO3801: Digital Defenders

## Installation

### For Linux:

1. **Install Docker and Docker Compose**  
   For Debian-based distributions:
   
   ```bash
   sudo apt install docker.io docker-compose
   ```

2. **Start the Docker service**  
   Use one of the following commands:
   
   ```bash
   sudo systemctl start docker
   ```
   or
   
   ```bash
   sudo service docker start
   ```

3. **Unzip the project**  
   Extract the contents of the project ZIP file to a desired directory on your machine.

4. **Create a Python virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

---

### For macOS:

1. **Install Docker and Docker Compose**  
   Download and install [Docker Desktop for macOS](https://www.docker.com/products/docker-desktop).

2. **Start Docker Desktop**  
   Docker Desktop should start automatically once installed. Ensure it is running by checking the menu bar.

3. **Unzip the project**  
   Extract the contents of the project ZIP file to a desired directory.

4. **Create a Python virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

### For Windows:

1. **Install Docker Desktop** from [here](https://www.docker.com/products/docker-desktop).

2. **Install Git Bash or any Bash-compatible terminal** if needed to run Bash commands (available [here](https://gitforwindows.org/)).

3. **Unzip the project**:  
   Extract the contents of the project ZIP file to a directory on your machine.

4. **Set up Python virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. **Install backend dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

---

### Starting the Project (will also build if there are no existing builds)

```bash
sudo docker-compose up -d
```

### Building/Rebuilding the Project

```bash
sudo docker-compose build
```

### Running and Rebuilding

```bash
sudo docker-compose up --build -d
```

### Viewing Logs (and errors)

```bash
sudo docker-compose logs
```

### Stopping the Containers

```bash
sudo docker-compose down
```

### Removing Stored Data (only if the containers are stopped)

```bash
sudo docker volume rm digital-defenders_db-data
```

### Accessing the Dashboard

Once started, open [http://localhost:8000](http://localhost:8000) in a browser to view the dashboard. You may need to run `sudo docker-compose up -d` multiple times during the first setup.

---

### Remove All Docker Images and Containers

```bash
sudo docker rm -vf $(sudo docker ps -aq)
sudo docker rmi -f $(sudo docker images -aq)
sudo docker volume prune -f
```

---

## Social Data Collection

Employers are expected to distribute a 63-question survey periodically (quarterly or bi-annually) to employees and upload the results to the dashboard's Social Risks page for data processing. A blank copy of the survey question/response spreadsheet can be found at `data/survey_blank.csv`. An example response file is available at `data/AI_survey_responses_80_employees.csv`. All uploaded CSV files must match this format.

---

## Active Users

The active users panel requires each user displayed to run the `monitoring.py` script, located in the `monitoring/` directory. Additional details are provided in the README file within this directory.
