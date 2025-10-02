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

## Setup Using Docker

1. Install docker and ensure its running
2. Build docker image
```powershell
docker build -t news-app:latest .
docker run -p 8000:8000 news-app:latest
```

## Sphinx
Documentation found in docs/build/html/index.html

```powershell
cd docs
make html
```
