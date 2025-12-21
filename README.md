# DevOps Notes Manager

A Flask-based web application to create, manage, and organize DevOps commands and notes.  
The application uses a MySQL database for persistence and follows secure configuration practices using environment variables.

---

## 🚀 Features

- Create, view, update, and delete DevOps notes
- MySQL database integration
- Clean and simple UI
- Environment variable–based configuration (no hardcoded secrets)
- Structured Flask backend with clear routing

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Environment Management:** python-dotenv
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

devops-notes-manager/
├── app.py
├── templates/
│ ├── index.html
│ └── edit.html
├── static/
│ └── css/
│ └── style.css
├── requirements.txt
├── .gitignore
└── .env # not committed

yaml
Copy code

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/devops-notes-manager.git
cd devops-notes-manager
2️⃣ Create and activate a virtual environment
bash
Copy code
python -m venv .venv
Windows (PowerShell):

powershell
Copy code
.\.venv\Scripts\Activate.ps1
Linux / macOS:

bash
Copy code
source .venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure environment variables
Create a .env file in the project root:

env
Copy code
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=devops_notes
⚠️ The .env file is ignored by Git and should never be committed.

5️⃣ Set up the MySQL database
sql
Copy code
CREATE DATABASE devops_notes;

USE devops_notes;

CREATE TABLE notes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  command VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
6️⃣ Run the application
bash
Copy code
python app.py
Open your browser and visit:

cpp
Copy code
http://127.0.0.1:5000
🔐 Security Notes
Database credentials are loaded using environment variables

Sensitive files such as .env and .venv are excluded via .gitignore

No secrets are committed to the repository

📌 Future Improvements
User authentication

Pagination for large datasets

Search and filtering

Dockerization (Flask + MySQL)

CI/CD integration

📄 License
This project is for learning and portfolio purposes.

yaml
Copy code

---
