This program runs on a user's computer, and supplies data for the users panel on the front page.  
It should work on both Windows and Linux. For Linux, make sure you have the net-tools package installed so that `netstat` is available, as this is a requirement for monitoring.py.  
By default, this program will try to connect to http://localhost:8000/api/userupdate, this can be changed by editing config.txt.
