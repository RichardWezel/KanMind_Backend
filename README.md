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
- Follow these steps to run the backend locally:

---


### 1. Clone the repository

```bash
git clone https://github.com/RichardWezel/KanMind_Backend.git
cd KanMind_Backend
```
---
### 2. Create and activate a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```
---
### 3. Install dependencies

```bash
pip install -r requirements.txt
```
---
### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```
---
### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```
---
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

## API Endpoint: User Registration

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            POST `/api/registration/`
        <span>
    </summary>
    <br>

Registers a new user account.

#### Request Body (JSON)
```json
{
  "fullname": "Example Username",
  "email": "example@mail.de",
  "password": "examplePassword",
  "repeated_password": "examplePassword"
}
```
#### Success Response (201 Created)

On successful registration, the API returns an authentication token and user details including the unique user ID.
```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```
#### Notes

- Password and repeated_password must match.
- The email must be unique and valid.
</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            POST `/api/login/`
        <span>
    </summary>
    <br>

Authenticates a user and returns an authentication token that is used for further API requests.

#### Request Body (JSON)
```json
{
  "email": "example@mail.de",
  "password": "examplePassword"
}
```
#### Success Response (201 Created)

On successful registration, the API returns an authentication token and user details including the unique user ID.
```json
{
  "token": "83bf098723b08f7b23429u0fv8274",
  "fullname": "Example Username",
  "email": "example@mail.de",
  "user_id": 123
}
```
#### Notes

/

</details>
<hr>

## API Endpoint: Boards

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/boards/`
        <span>
    </summary>
    <br>

Retrieves a list of boards that the logged-in user has either created or is a member of.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### Success Response (201 Created)

The response contains a list of the boards with the basic information: Title, ID of the owner and the number of members, the general task count and the number of tasks in ‘to-do’ and with priority ‘high’.

```json
[
  {
    "id": 1,
    "title": "Projekt X",
    "member_count": 2,
    "ticket_count": 5,
    "tasks_to_do_count": 2,
    "tasks_high_prio_count": 1,
    "owner_id": 12
  },
  {
    "id": 1,
    "title": "Projekt Y",
    "member_count": 12,
    "ticket_count": 43,
    "tasks_to_do_count": 12,
    "tasks_high_prio_count": 1,
    "owner_id": 3
  }
]
```
#### Notes

- Permissions required: The user must be a member of one of the boards or the owner of a board in order to view it.
- Die Liste der Boards enthält nur die Boards, zu denen der authentifizierte Benutzer Zugriff hat.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            POST `/api/boards/`
        <span>
    </summary>
    <br>


Creates a new board and adds members. The user is automatically created as the owner and can add themselves as a member

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### Request Body (JSON)
```json
{
  "title": "Neues Projekt",
  "members": [
    12,
    5,
    54,
    2
  ]
}
```
#### Success Response (201 Created)

The response contains the newly created board with the basic information: Title, ID of the owner and a list of members.
```json
{
  "id": 18,
  "title": "neu",
  "member_count": 4,
  "ticket_count": 0,
  "tasks_to_do_count": 0,
  "tasks_high_prio_count": 0,
  "owner_id": 2
}
```
#### Notes

Permissions required: The user must be logged in to create a new board.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/boards/{board_id}/`
        <span>
    </summary>
    <br>

Retrieves the information of a specific board, together with the associated tasks.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`board_id`:`The ID of the board whose information and assigned tasks are to be retrieved.`

#### Success Response (201 Created)

The response contains the board information (title, members) and the tasks assigned to the board.
```json
{
  "id": 1,
  "title": "Projekt X",
  "owner_id": 12,
  "members": [
    {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    {
      "id": 54,
      "email": "max.musterfrau@example.com",
      "fullname": "Maxi Musterfrau"
    }
  ],
  "tasks": [
    {
      "id": 5,
      "title": "API-Dokumentation schreiben",
      "description": "Die API-Dokumentation für das Backend vervollständigen",
      "status": "to-do",
      "priority": "high",
      "assignee": null,
      "reviewer": {
        "id": 1,
        "email": "max.mustermann@example.com",
        "fullname": "Max Mustermann"
      },
      "due_date": "2025-02-25",
      "comments_count": 0
    },
    {
      "id": 8,
      "title": "Code-Review durchführen",
      "description": "Den neuen PR für das Feature X überprüfen",
      "status": "review",
      "priority": "medium",
      "assignee": {
        "id": 1,
        "email": "max.mustermann@example.com",
        "fullname": "Max Mustermann"
      },
      "reviewer": null,
      "due_date": "2025-02-27",
      "comments_count": 0
    }
  ]
}
```
#### Notes

- Permissions required: The user must either be a member of the board or the owner of the board in order to access the information and tasks.
- The response contains the board with all members and the associated tasks.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            PATCH `/api/boards/{board_id}/`
        <span>
    </summary>
    <br>

Updates the members of an existing board. Members can be added or removed. The user making the request must be either the owner of the board or a member of the board. This endpoint is not intended for changing tasks!

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`board_id`:`The ID of the board whose members are to be updated.`

#### Request Body (JSON)
```json
{
  "title": "Changed title",
  "members": [
    1,
    54
  ]
}
```
#### Success Response (201 Created)

The response contains the updated board with the new members and removes unnamed members.

```json
{
  "id": 3,
  "title": "Changed title",
  "owner_data": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "members_data": [
    {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    {
      "id": 54,
      "email": "max.musterfrau@example.com",
      "fullname": "Maxi Musterfrau"
    }
  ]
}
```
#### Notes

- Permissions required: The user must be either the owner or a member of the board to add or remove members.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            DELETE `/api/boards/{board_id}/`
        <span>
    </summary>
    <br>


Deletes a board. Only the owner of the board is authorized to delete the board.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`board_id`:`The ID of the board to be deleted.`

#### Success Response (201 Created)

The response confirms that the board has been successfully deleted.
```
null
```
#### Notes

- Permissions required: The user must be the owner of the board to delete it.
- Wenn der Benutzer nicht der Eigentümer des Boards ist, wird die Anfrage mit einem `401 Unauthorized`-Fehler abgelehnt. Das Löschen eines Boards entfernt alle zugehörigen Tasks und Kommentare.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/email-check/`
        <span>
    </summary>
    <br>

Checks whether a specific e-mail address is already assigned to a registered user.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`email`:`The e-mail address to be checked.`

#### Success Response (201 Created)

The response returns the user if it exists.
```json
{
  "id": 1,
  "email": "max.mustermann@example.com",
  "fullname": "Max Mustermann"
}
```
#### Notes

- Permissions required: The user must be logged in

</details>
<hr>

## API Endpoint: Tasks

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/tasks/assigned-to-me/`
        <span>
    </summary>
    <br>

Retrieves all tasks that are assigned to the currently authenticated user either as an assignee. The user must be logged in to access these tasks.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### Success Response (201 Created)

The response contains a list of tasks that have either been assigned to the currently authenticated user. Each task contains basic information such as title, status, priority and due date.
```json
{
{
    "id": 1,
    "board": 1,
    "title": "Task 1",
    "description": "Beschreibung der Task 1",
    "status": "to-do",
    "priority": "high",
    "assignee": {
      "id": 13,
      "email": "marie.musterfraun@example.com",
      "fullname": "Marie Musterfrau"
    },
    "reviewer": {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    "due_date": "2025-02-25",
    "comments_count": 0
  },
  {
    "id": 2,
    "board": 12,
    "title": "Task 2",
    "description": "Beschreibung der Task 2",
    "status": "in-progress",
    "priority": "medium",
    "assignee": {
      "id": 13,
      "email": "marie.musterfraun@example.com",
      "fullname": "Marie Musterfrau"
    },
    "reviewer": null,
    "due_date": "2025-02-20",
    "comments_count": 0
  }
}
```
#### Notes

- Permissions required: The user must be logged in and authenticated in order to access the tasks assigned to them as an assignee.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/tasks/reviewing/`
        <span>
    </summary>
    <br>

Retrieves all tasks for which the currently authenticated user is entered as a reviewer (`reviewer`). The user must be logged in to access these tasks.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### Success Response (201 Created)

The response contains a list of tasks that have been assigned to the authenticated user for review. Each task contains basic information such as title, status, priority and due date.
```json
{
{
    "id": 1,
    "board": 1,
    "title": "Task 1",
    "description": "Beschreibung der Task 1",
    "status": "to-do",
    "priority": "high",
    "assignee": null,
    "reviewer": {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    "due_date": "2025-02-25",
    "comments_count": 0
  },
  {
    "id": 2,
    "board": 12,
    "title": "Task 2",
    "description": "Beschreibung der Task 2",
    "status": "in-progress",
    "priority": "medium",
    "assignee": {
      "id": 13,
      "email": "marie.musterfraun@example.com",
      "fullname": "Marie Musterfrau"
    },
    "reviewer": {
      "id": 1,
      "email": "max.mustermann@example.com",
      "fullname": "Max Mustermann"
    },
    "due_date": "2025-02-20",
    "comments_count": 0
  }
}
```
#### Notes

- Permissions required: The user must be logged in and authenticated to access the tasks assigned to him as a reviewer.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            POST `/api/tasks/`
        <span>
    </summary>
    <br>

Creates a new task within a board. The user must use one of the following values for the status: `to-do`, `in-progress`, `review` or `done` and one of the following values for the priority: `low`, `medium` or `high`.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### Request Body (JSON)
```json
{
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-27"
}
```
#### Success Response (201 Created)

The response contains the created task with all associated information.
```json
{
  "id": 10,
  "board": 12,
  "title": "Code-Review durchführen",
  "description": "Den neuen PR für das Feature X überprüfen",
  "status": "review",
  "priority": "medium",
  "assignee": {
    "id": 13,
    "email": "marie.musterfraun@example.com",
    "fullname": "Marie Musterfrau"
  },
  "reviewer": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "due_date": "2025-02-27",
  "comments_count": 0
}
```
#### Notes

- Permissions required: The user must be a member of the board to create a task.
- Both `assignee` and `reviewer` must be members of the board. If no `assignee` or `reviewer` is specified, the field remains empty.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
           PATCH `/api/tasks/{task_id}/`
        <span>
    </summary>
    <br>

Updates an existing task. Only members of the board to which the task belongs can edit it.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`task_id`:`The ID of the task to be updated.`

#### Request Body (JSON)
```json
{
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee_id": 13,
  "reviewer_id": 1,
  "due_date": "2025-02-28"
}
```
#### Success Response (201 Created)

The response contains the updated task with all changed values.
```json
{
  "id": 10,
  "title": "Code-Review abschließen",
  "description": "Den PR fertig prüfen und Feedback geben",
  "status": "done",
  "priority": "high",
  "assignee": {
    "id": 13,
    "email": "marie.musterfraun@example.com",
    "fullname": "Marie Musterfrau"
  },
  "reviewer": {
    "id": 1,
    "email": "max.mustermann@example.com",
    "fullname": "Max Mustermann"
  },
  "due_date": "2025-02-28"
}
```
#### Notes

- Permissions required: The user must be a member of the board in order to update a task. Changing the board id(board) is not allowed!
- Felder, die nicht aktualisiert werden sollen, können weggelassen werden. `assignee` und `reviewer` müssen weiterhin Mitglieder des Boards sein.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
           DELETE `/api/tasks/{task_id}/`
        <span>
    </summary>
    <br>

Deletes an existing task. Only the creator of the task or the owner of the board can delete the task.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`task_id`:`The ID of the task to be deleted.`

#### Success Response (201 Created)

If the task was successfully deleted, a confirmation without content is returned.
```
null
```
#### Notes

- Permissions required: Only the creator of the task or the owner of the board can delete a task.
- The deletion is permanent and cannot be undone.

</details>
<hr>

<details>
<summary>
        <span style="font-size: 16px; font-weight: bold;">
            GET `/api/tasks/{task_id}/comments/`
        <span>
    </summary>
    <br>

Retrieves all comments that are assigned to a specific task.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`task_id`:`The ID of the task for which the comments are to be retrieved.`

#### Success Response (201 Created)

The response contains a list of all comments on the specified task. Each comment contains the creation date, the full name of the author and the content.
```json
[
  {
    "id": 1,
    "created_at": "2025-02-20T14:30:00Z",
    "author": "Max Mustermann",
    "content": "Das ist ein Kommentar zur Task."
  },
  {
    "id": 2,
    "created_at": "2025-02-21T09:15:00Z",
    "author": "Erika Musterfrau",
    "content": "Ein weiterer Kommentar zur Diskussion."
  }
]
```
#### Notes

- Permissions required: The user must be a member of the board to which the task belongs.
- The comments are sorted chronologically by date of creation.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
            POST `/api/tasks/{task_id}/comments/`
        <span>
    </summary>
    <br>

Creates a new comment for a specific task. The author is determined automatically based on the authentication.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`task_id`:`The ID of the task to which the comment is to be added.`

#### Request Body (JSON)
```json
{
  "content": "Das ist ein neuer Kommentar zur Task."
}
```
#### Success Response (201 Created)

The response contains the created comment instance with ID, creation date, full name of the author and the content.
```json
{
  "id": 15,
  "created_at": "2025-02-20T15:00:00Z",
  "author": "Max Mustermann",
  "content": "Das ist ein neuer Kommentar zur Task."
}
```
#### Notes

- Permissions required: The user must be a member of the board to which the task belongs.
- The author of the comment is determined from the authentication of the current user.

</details>
<hr>

<details>
    <summary>
        <span style="font-size: 16px; font-weight: bold;">
           DELETE `/api/tasks/{task_id}/comments/{comment_id}/`
        <span>
    </summary>
    <br> 

Deletes a comment from a specific task. Only the creator of the comment can delete it.

#### Headers

The following HTTP headers are required for this request:

- `Content-Type`: `application/json`
- `Authorization`: `Token <your-authentication-token>`

#### URL Parameters

`task_id`:`The ID of the task to which the comment belongs.`
`comment_id`:`The ID of the comment to be deleted.`

#### Success Response (201 Created)

If the deletion is successful, an empty response with status code `204` is returned.
```
null
```
#### Notes

- Permissions required: Only the user who created the comment may delete it.
- If the comment or task does not exist, a `404` error is returned.


