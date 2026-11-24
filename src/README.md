# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Create clubs with an advisor, schedule, location, and membership capacity
- Change a club's advisor, membership capacity, and active status
- Sign up for active clubs with available spaces
- Unregister students from activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all clubs, status, advisor, capacity, and participants          |
| GET    | `/professors`                                                      | List professors who can advise clubs                                |
| POST   | `/activities`                                                      | Create a club                                                       |
| PATCH  | `/activities/{activity_name}`                                      | Update a club's advisor, capacity, or active status                 |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an active club with available spaces                    |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from a club                                  |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Clubs** - Uses club name as identifier:

   - Description
   - Schedule
   - Location and professor advisor
   - Active status and maximum membership capacity
   - List of student emails who are signed up

2. **Professors** - A list of eligible club advisors identified by email.

All data is stored in memory, which means new clubs and membership changes reset when the server restarts.
