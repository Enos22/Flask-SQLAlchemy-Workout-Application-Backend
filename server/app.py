from datetime import date

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate

from models import  Workout, WorkoutExercise, Exercise, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Define Routes here

@app.route("/workouts", methods = ["GET"])
def get_workouts():
    workouts = Workout.query.all()

    workout_list = []
    for w in workouts:
        workout_list.append({
            "id": w.id,
            "date": w.date.isoformat() if w.date else None,
            "duration_minutes": w.duration_minutes,
            "notes": w.notes
        })
    return jsonify(workout_list), 200

@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = Workout.query.filter_by(id=id).first()
    if not workout:
        return jsonify({"error": "Workout Not Found!"}), 404

    workout_all = {
        "id": workout.id,
        "date": workout.date.isoformat() if workout.date else None,
        "duration_minutes": workout.duration_minutes,
        "notes": workout.notes,
        "workout_exercises": []
    }
#alias workout_exercises as we, access and display
    for we in workout.WorkoutExercises:
        exercise = we.exercise
        exercise_details = {
            "exercise_id": exercise.id if exercise else None,
            "exercise_name": exercise.name if exercise else None,
            "reps": we.reps,
            "sets": we.sets,
            "duration": we.duration_seconds,
            "duration_seconds": we.duration_seconds
        }
        workout_all["workout_exercises"].append(exercise_details)

    return jsonify(workout_all), 200

# POST /workouts
# Create a workout
@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    workout_date = data.get("date")
    if workout_date:
        try:
            workout_date = date.fromisoformat(workout_date)
        except ValueError:
            return jsonify({"error": "Date must be in YYYY-MM-DD format."}), 400

    new_workout = Workout(
        date=workout_date,
        duration_minutes=data.get("duration_minutes"),
        notes=data.get("notes")
    )
    db.session.add(new_workout)
    db.session.flush()

    exercises_data = data.get("workout_exercises", [])
    for ed in exercises_data:
        workout_exercise = WorkoutExercise(
            workout_id=new_workout.id,
            exercise_id=ed.get("exercise_id"),
            reps=ed.get("reps"),
            sets=ed.get("sets"),
            duration_seconds=ed.get("duration_seconds")
        )
        db.session.add(workout_exercise)

    db.session.commit()

    workout_dict = {
        "id": new_workout.id,
        "date": new_workout.date.isoformat() if new_workout.date else None,
        "duration_minutes": new_workout.duration_minutes,
        "notes": new_workout.notes,
        "workout_exercises": []
    }

    for we in new_workout.WorkoutExercises:
        exercise = we.exercise
        exercise_details = {
            "exercise_id": exercise.id if exercise else None,
            "exercise_name": exercise.name if exercise else None,
            "reps": we.reps,
            "sets": we.sets,
            "duration_seconds": we.duration_seconds
        }
        workout_dict["workout_exercises"].append(exercise_details)

    return jsonify(workout_dict), 201
    


if __name__ == '__main__':
    app.run(port=5555, debug=True)