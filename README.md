# Flask SQLAlchemy Workout Application Backend

## Project Description
This project is a Flask API for managing workouts and exercises. It uses Flask-SQLAlchemy to model the database and Marshmallow schemas to validate incoming request data and serialize API responses. 
The API supports creating, retrieving, and deleting workouts and exercises, as well as linking exercises to workouts.

## Features
- Manage workout records with dates, duration, and notes
- Manage exercise records with categories and equipment requirements
- Associate exercises with workouts through a join table
- Validate request payloads with Marshmallow
- Seed the database with sample workout data

## Installation
From the project root, install the project dependencies with Pipenv:

```bash
pipenv install
```

If the project database has not been created yet, initialize the Flask app database and apply migrations:

```bash
cd server
pipenv shell
flask db upgrade head
```

To populate the database with sample data, run the seed script:

```bash
cd server
pipenv shell(if not)
python3 seed.py
```

If you need to recreate the database from scratch, delete the existing SQLite database file and rerun the migration/seed process as needed.

## Run Instructions
Start the Flask server from the server directory:

```bash
cd server
pipenv run flask --app app run
```

You can also run the app directly:

```bash
cd server
pipenv shell(if not)
python3 app.py
```

The app is configured to run on port `5555` when started with `python app.py`.

## API Endpoints
Base URL: `http://localhost:5555` when using `python3 app.py`.

### Workouts

#### GET /workouts
Returns all workout records.

Example response:
```json
[
  {
    "id": 1,
    "date": "2024-01-02",
    "duration_minutes": 40,
    "notes": "Leg day",
    "workout_exercises": []
  }
]
```

#### GET /workouts/<id>
Returns a single workout by its ID, including its associated exercises.

#### POST /workouts
Creates a new workout.

Required fields:
- `date` (YYYY-MM-DD)
- `duration_minutes` (must be at least 1)
- `notes` (required and non-empty)
- optional `workout_exercises` list with entries containing `exercise_id`, `reps`, `sets`, and `duration_seconds`

#### DELETE /workouts/<id>
Deletes a workout by ID.

### Exercises

#### GET /exercises
Returns all exercise records.

#### GET /exercises/<id>
Returns a single exercise by ID, including the workouts it is linked to.

#### POST /exercises
Creates a new exercise.

Required fields:
- `name` (required and non-empty)
- `category` (required and non-empty)
- optional `equipment_needed` (boolean, defaults to `false`)
- optional `workout_exercises` list used to create workout-to-exercise links

#### DELETE /exercises/<id>
Deletes an exercise by ID and removes its related workout links.

### Workout Exercise Assignment

#### POST /workouts/<workout_id>/exercise/<exercise_id>/workout_excercises
Assigns an exercise to a workout.

Required request JSON fields:
- `reps` (must be at least 1)
- `sets` (must be at least 1)
- `duration_seconds` (must be at least 1)

This endpoint prevents duplicate assignments by returning a `409 Conflict` error if that exercise is already assigned to the same workout.

## Database Notes
The project uses SQLite by default for local development. 
The app is set up with Flask-Migrate, so database changes can be managed through migration files in the `server/migrations` directory.

## Example Workflow
```bash
cd server
pipenv install
pipenv shell
` ` ` ` flask db upgrade head
` ` ` ` python3 seed.py
` ` ` `python3 app.py
```
