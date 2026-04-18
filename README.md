# Deception-Based IDS
This project is a deception-based intrusion detection application that identifies suspicious login behavior and redirects attackers into a controlled honeypot environment. The system emphasizes usability by providing both beginner-friendly summaries and advanced technical logs.

Requirements:
  * Python 3.10 +
  * Web browser
  * Python Flask
    * pip install flask
      
Project Folder Structure:
    Main_project
    |-- app.py
    |-- dashboard.py
    |--logs/
        |-- events.log (code will create if not exist)
    |--templates
        |-- login.html
        |-- decoy.html
        |--dashboard.html
    |-- run_app.bat
    
Installation:
  Clone repository
  Navigate to the project folder
  install dependencies
    * pip install flask
  Double-click run_app.bat to run the website on 2 different terminals
            OR
  run in separate terminals -- python app.py -- python dashboard.py
      Then open:
                http://127.0.0.1:5000 --login interface
                http://127.0.0.1:5001 --security dashboard
              
