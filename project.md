# PROJECT: Dental Clinic Telegram Bot System

## 1. General Description

System consists of:
- Telegram Bot
- Backend API
- Admin Panel
- PostgreSQL database
- Integration with Bitrix24
- Auto deployment via GitHub

AI features are NOT included.

---

## 2. Tech Stack

Language: Python 3.11  
Framework: FastAPI  
Bot Framework: aiogram 3.x  
Database: PostgreSQL  
ORM: SQLAlchemy 2.0  
Migrations: Alembic  
Templating: Jinja2  
Auth: JWT  
Server: Ubuntu 22.04  
Web Server: Nginx  
Process manager: systemd

---

## 3. Functional Requirements

### 3.1 User Flow

User enters bot via quiz link:

https://t.me/dentalcgroup_bot?start=SOURCE_DATA

Bot must:

- Parse start parameter
- Save:
    - full_name
    - username
    - phone
    - source
    - form_name
    - utm_source
    - utm_medium
    - utm_campaign
- Assign:
    - status = active
    - created_at timestamp

---

### 3.2 Database Models

#### User
- id
- telegram_id
- full_name
- username
- phone
- is_active (boolean)
- source
- form_name
- utm_source
- utm_medium
- utm_campaign
- created_at

#### Group
- id
- name

#### UserGroup
- id
- user_id
- group_id

#### Mailing
- id
- title
- content
- media_path
- created_at

---

### 3.3 Admin Panel Features

Admin must:

- View all users
- Filter users by:
    - source
    - active status
    - group
    - date
- Enable / disable user
- Create groups
- Assign users to groups
- Create mailings:
    - text
    - image
    - video
    - inline buttons
- Send mailing to:
    - all users
    - specific group
- View mailing statistics

---

### 3.4 Bot Menu

Main menu must include:

- Get Consultation
- Call Clinic
- Our Location

Menu must be configurable from database.

---

### 3.5 Notifications

When new user registers:
- Notify admin chat

---

### 3.6 Bitrix24 Integration

When:
- user leaves phone

System must:
- Create lead in Bitrix24 via REST API

---

## 4. Project Structure

app/
main.py
config.py
database.py

    bot/
    api/
    admin/
    models/
    services/

alembic/
project.md
requirements.txt

---

## 5. Deployment Rules

- Code deployed via GitHub Actions
- On push to main:
    - git pull
    - pip install
    - alembic upgrade
    - restart service

---

## 6. Security

- Admin auth required
- Password hashing via bcrypt
- JWT tokens
- Environment variables in .env
- No secrets in repo

---

## 7. Scaling Strategy

Stage 1:
- Single server

Stage 2:
- Add Redis
- Add Celery
- Split bot and API processes

Stage 3:
- Add load balancing