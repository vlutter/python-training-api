from api import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    example_data = db.Column(db.String(2048))
    group_id = db.Column(db.Integer, db.ForeignKey('task_group.id'), nullable=False)

    group = db.relationship('TaskGroup', back_populates='tasks')


class TaskGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    tasks = db.relationship('Task', back_populates='group')
