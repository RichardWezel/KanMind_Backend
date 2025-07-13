# KanMind

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

KanMind is a Kanban board application built with **Django** and the **Django REST Framework**. It allows users to collaboratively manage tasks within boards. Each board can have multiple members, tasks can be created, updated, commented on, and moved between different status columns such as:

- To Do  
- In Progress  
- Review  
- Done

This project is designed for **teams** that want to coordinate work and keep track of task progress in a structured and visual way.

**GitHub Repository:**  
[https://github.com/RichardWezel/KanMind_Backend.git](https://github.com/RichardWezel/KanMind_Backend.git)

---

## Tech Stack

- Python 3
- Django 5.2.3
- Django REST Framework 3.16.0

All dependencies are listed in [`requirements.txt`](./requirements.txt).

---

## Getting Started

Follow these steps to run the backend locally:

### 1. Clone the repository

```bash
git clone https://github.com/RichardWezel/KanMind_Backend.git
cd KanMind_Backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

---

## Project Structure

```plaintext
KanMind_Backend/
│
├── core/               # Project settings and root urls.py
│
├── auth_app/           # Handles user registration and login
│   └── api/
│       ├── views.py
│       ├── urls.py
│       ├── serializers.py
│       └── permissions.py
│
├── boards_app/         # Contains board logic and membership
│   └── api/
│       ├── views.py
│       ├── urls.py
│       ├── serializers.py
│       └── permissions.py
│
├── tasks_app/          # Manages tasks and comments
│   └── api/
│       ├── views.py
│       ├── urls.py
│       ├── serializers.py
│       └── permissions.py
```

There are no example users included.

---

## Frontend

A separate frontend application exists and must be downloaded individually. It communicates with this Django backend via RESTful APIs.

---

## Docker

This project does not use Docker.

---

## Tests

Currently, there are no automated tests.

---

## Background

KanMind was originally developed as part of a developer training program to teach the fundamentals of Django and Django REST Framework. It represents a beginner’s first complete backend and follows a predefined documentation with a checklist and required endpoints.

---
