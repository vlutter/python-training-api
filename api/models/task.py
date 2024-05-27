from api import db


class Task(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(4096))
    tests = db.Column(db.String(4096))
    group_id = db.Column(db.Integer, db.ForeignKey('task_group.id'), nullable=False)

    group = db.relationship('TaskGroup', back_populates='tasks')
    solutions = db.relationship('Solution', back_populates='task', cascade="all, delete-orphan")


class Solution(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    task_id = db.Column(db.String(100), db.ForeignKey('task.id'), primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    last_solution = db.Column(db.String(4096))
    last_output = db.Column(db.String(4096))

    user = db.relationship('User', back_populates='solutions')
    task = db.relationship('Task', back_populates='solutions')


class TaskGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    tasks = db.relationship('Task', back_populates='group')
