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


#delete a wokout
@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = Workout.query.filter_by(id=id).first()

   # global workouts
    # workout = next((w for w in workouts if w.id ==id), None)

    if not workout:
        return("Workout Not Found", 404)
    db.session.delete(workout)
    db.session.commit()

    return("Workout deleted", 204)

#lst all exercises
@app.route("/exercises", methods = ["GET"])
def get_exercises():
    exercises = Exercise.query.all()

    excercise_list = []
    for e in exercises:
        excercise_list.append({
            "id": e.id,
            "name": e.name,
            "category": e.category,
            "equipment_needed": e.equipment_needed
        })

    return jsonify(excercise_list), 200

#list excercises with associated workouts
@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = Exercise.query.filter_by(id=id).first()
    if not exercise:
        return jsonify({"error": "Exercise Not Found!"}), 404

    exercise_data = {
        "id": exercise.id,
        "name": exercise.name,
        "category": exercise.category,
        "equipment_needed": exercise.equipment_needed,
        "workouts": []
    }
    for ew in exercise.WorkoutExercises:
        workout = ew.workout
        if not workout:
            continue

        exercise_data["workouts"].append({
            "workout_id": workout.id,
            "workout_date": workout.date.isoformat() if workout.date else None,
            "notes": workout.notes,
            "duration_minutes": workout.duration_minutes,
            "reps": ew.reps,
            "sets": ew.sets,
            "duration_seconds": ew.duration_seconds
        })

    return jsonify(exercise_data), 200

#create exercise

@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    exercise_name = data.get("name")
    category = data.get("category")
    if not exercise_name or not category:
        return jsonify({"error": "Exercise name and category are required."}), 400

    equipment_needed = data.get("equipment_needed", False)

    try:
        new_exercise = Exercise(
            name=exercise_name,
            category=category,
            equipment_needed=bool(equipment_needed)
        )
        db.session.add(new_exercise)
        db.session.flush()

        exercises_data = data.get("workout_exercises", [])
        if exercises_data is not None and not isinstance(exercises_data, list):
            return jsonify({"error": "workout_exercises must be a list."}), 400

        for ed in exercises_data:
            if not isinstance(ed, dict):
                return jsonify({"error": "Each workout_exercise entry must be an object."}), 400

            workout_id = ed.get("workout_id")
            if workout_id is None:
                return jsonify({"error": "workout_id is required for each workout_exercise."}), 400

            workout = Workout.query.filter_by(id=workout_id).first()
            if not workout:
                return jsonify({"error": f"Workout {workout_id} not found."}), 404

            reps = ed.get("reps")
            sets = ed.get("sets")
            duration_seconds = ed.get("duration_seconds")
            if reps is None or sets is None or duration_seconds is None:
                return jsonify({"error": "reps, sets, and duration_seconds are required for each workout_exercise."}), 400

            workout_exercise = WorkoutExercise(
                exercise_id=new_exercise.id,
                workout_id=workout_id,
                reps=reps,
                sets=sets,
                duration_seconds=duration_seconds
            )
            db.session.add(workout_exercise)

        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Unable to create exercise."}), 400

    exercise_dict = {
        "id": new_exercise.id,
        "name": new_exercise.name,
        "category": new_exercise.category,
        "equipment_needed": new_exercise.equipment_needed,
        "workout_exercises": []
    }

    for we in new_exercise.WorkoutExercises:
        exercise = we.exercise
        exercise_details = {
            "exercise_id": exercise.id if exercise else None,
            "exercise_name": exercise.name if exercise else None,
            "workout_id": we.workout_id,
            "reps": we.reps,
            "sets": we.sets,
            "duration_seconds": we.duration_seconds
        }
        exercise_dict["workout_exercises"].append(exercise_details)

    return jsonify(exercise_dict), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.filter_by(id=id).first()
    if not exercise:
        return jsonify({"error": "Exercise Not Found!"}), 404

    for workout_exercise in list(exercise.WorkoutExercises):
        db.session.delete(workout_exercise)

    db.session.delete(exercise)
    db.session.commit()

    return "Exercise deleted", 204

@app.route("/workouts/<int:workout_id>/exercise/<int:exercise_id>/workout_excercises", methods=["POST"])
def create_all(workout_id, exercise_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    workout = Workout.query.filter_by(id=workout_id).first()
    if not workout:
        return jsonify({"error": "Workout not found."}), 404

    exercise = Exercise.query.filter_by(id=exercise_id).first()
    if not exercise:
        return jsonify({"error": "Exercise not found."}), 404

    reps = data.get("reps")
    sets = data.get("sets")
    duration_seconds = data.get("duration_seconds")

    if reps is None or sets is None or duration_seconds is None:
        return jsonify({"error": "reps, sets, and duration_seconds are required."}), 400

    existing_link = WorkoutExercise.query.filter_by(workout_id=workout_id, exercise_id=exercise_id).first()
    if existing_link:
        return jsonify({"error": "This exercise is already assigned to this workout."}), 409

    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        reps=reps,
        sets=sets,
        duration_seconds=duration_seconds
    )
    db.session.add(workout_exercise)
    db.session.commit()

    return jsonify({
        "id": workout_exercise.id,
        "workout_id": workout_exercise.workout_id,
        "exercise_id": workout_exercise.exercise_id,
        "reps": workout_exercise.reps,
        "sets": workout_exercise.sets,
        "duration_seconds": workout_exercise.duration_seconds
    }), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)