# Online Voting System

A web-based voting system built with **Flask** and **SQLite**. Students register, log in, and cast one vote per election. Admins create elections, add candidates, open or close voting, and view results.

## Features

**Voter**
- Register and log in with Student ID and password
- View open elections and their candidates
- Cast one vote per election (double voting is blocked)

**Admin**
- Create elections and add candidates
- Open or close an election
- View results for each election

## Security

- Passwords are hashed and never stored in plain text
- Double voting is prevented at the database level with a composite primary key
- Voter identity (`ballots_cast`) is stored separately from the vote (`votes`), so ballots stay anonymous
- Role-based access control protects admin pages
- Parameterized SQL queries prevent SQL injection
- The secret key is read from an environment variable instead of being hard-coded

## Tech Stack

- Python 3, Flask
- SQLite
- HTML, Jinja2 templates, Bootstrap 5

## Project Structure

```
Online-voting-system/
├── app.py              # Flask application (routes and logic)
├── init_db.py          # Creates the database and the admin account
├── schema.sql          # Database tables
├── requirements.txt    # Python dependencies
├── .gitignore
├── README.md
└── templates/
    ├── base.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── vote.html
    ├── admin.html
    └── results.html
```

## Database Design

| Table | Purpose |
|---|---|
| `users` | Student details, hashed password, and role (voter or admin) |
| `elections` |
