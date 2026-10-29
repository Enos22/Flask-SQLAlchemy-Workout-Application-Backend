#!/usr/bin/env python3

from app import app
from datetime import date
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    # reset data safely in dependency order so no FK errors or duplicates remain
    db.session.query(WorkoutExercise).delete()
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()
    db.session.commit()

    exercises = [
        Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False
        ),
        Exercise(
            name="Running",
            category="Cardio",
            equipment_needed=False
        ),
        Exercise(
            name="Dumbbell Curls",
            category="Strength",
            equipment_needed=True
        ),
        Exercise(
            name="Plank",
            category="Core",
            equipment_needed=False
        ),
        Exercise(
            name="Cycling",
            category="Cardio",
            equipment_needed=True
        )
    ]
    # exercises = []



    db.session.add_all(exercises)
    db.session.commit()


    workout1 = Workout(
            date=date(2026, 10, 20),
            duration_minutes=45,
            notes="Morning strength training"
        )

    workout2 = Workout(
            date=date(2026, 10, 21),
            duration_minutes=30,
            notes="Cardio and core training"
        )

    db.session.add_all([workout1, workout2])
    db.session.commit()

    workout_exercises = [
        WorkoutExercise(
                workout_id=workout1.id,
                exercise_id=exercises[0].id,
                reps=15,
                sets=3,
                duration_seconds=30
            ),
            WorkoutExercise(
                workout_id=workout1.id,
                exercise_id=exercises[2].id,
                reps=12,
                sets=3,
                duration_seconds=45
            ),
            WorkoutExercise(
                workout_id=workout2.id,
                exercise_id=exercises[1].id,
                reps=15,
                sets=2,
                duration_seconds=1200
            ),
            WorkoutExercise(
                workout_id=workout2.id,
                exercise_id=exercises[3].id,
                reps=10,
                sets=3,
                duration_seconds=60
            )
        ]

    db.session.add_all(workout_exercises)
    db.session.commit()