# News App

A Django-based news application where users can be Readers, Journalists, Editors, or Publishers.  
This project supports both local virtual environment setup and Docker-based deployment.

---

## Features

- Custom user roles: Reader, Journalist, Editor, Publisher  
- Article and Newsletter management  
- Drafts, approvals, and publishing workflow  
- REST API for articles, drafts, and publishers  
- Fully documented using Sphinx  

---

## Setup Using Virtual Environment

1. Clone the repository:
```powershell
git clone https://github.com/Chie-codes/News_app
cd news_project
```
2. Create and activate virtual environment
```powershell
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

```
3. Install dependencies
```powershell
pip install -r requirements.txt
```
4. Run migration
```powershell
python manage.py makemigrations
python manage.py migrate
```
5. Create a superuser
```powershell
python manage.py createsuperuser
```
6. Start server
```powershell
python manage.py runserver
```

## Setup Using Docker Compose

1. Make sure Docker is installed and running.
2. From the root of your project, build and start the containers:

```powershell
docker compose up --build
```
This will:

- Build the Django app image
- Start the MySQL database container
- Run makemigrations and migrate automatically
- Run the Django development server on http://localhost:8000

3. To stop and remove containers and volumes:

```powershell
docker compose down -v
```

## Sphinx
Documentation found in docs/build/html/index.html

```powershell
cd docs
make html
```
