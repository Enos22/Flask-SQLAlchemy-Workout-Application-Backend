from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Define Models here



class Exercise(db.Model):
    __tablename__='exercise'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    category = db.Column(db.String, nullable = False)
    equipment_needed = db.Column(db.Boolean, default = False, nullable = False)

    WorkoutExercises = db.relationship('WorkoutExercise', back_populates = 'exercise')
    workouts = db.relationship('Workout', secondary='workoutexercise', back_populates='exercises', viewonly=True)

class Workout(db.Model):
    __tablename__='workout'

    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    duration_minutes = db.Column(db.Integer, nullable = False)
    notes = db.Column(db.Text, nullable = False)

    WorkoutExercises = db.relationship('WorkoutExercise', back_populates = 'workout')
    exercises = db.relationship('Exercise', secondary='workoutexercise', back_populates='workouts', viewonly=True)


class WorkoutExercise(db.Model):
    __tablename__='workoutexercise'

    id = db.Column(db.Integer, primary_key = True)
    workout_id =db.Column(db.Integer, db.ForeignKey('workout.id'))
    exercise_id =db.Column(db.Integer, db.ForeignKey('exercise.id'))
    reps = db.Column(db.Integer, nullable = False)
    sets = db.Column(db.Integer, nullable = False)
    duration_seconds = db.Column(db.Integer, nullable = False)

    workout = db.relationship('Workout', back_populates = 'WorkoutExercises')
    exercise = db.relationship('Exercise', back_populates = 'WorkoutExercises')


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    category = fields.String(required=True, validate=validate.Length(min=1))
    equipment_needed = fields.Boolean(load_default=False)
    workout_exercises = fields.List(fields.Dict(), load_default=list, dump_default=list)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.String(required=True, validate=validate.Length(min=1))
    workout_exercises = fields.List(fields.Dict(), load_default=list, dump_default=list)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True, validate=validate.Range(min=1))
    exercise_id = fields.Int(required=True, validate=validate.Range(min=1))
    reps = fields.Int(required=True, validate=validate.Range(min=1))
    sets = fields.Int(required=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=1))

    
