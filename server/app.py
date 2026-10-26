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



if __name__ == '__main__':
    app.run(port=5555, debug=True)