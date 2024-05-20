from api import db


class Task(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    tests = db.Column(db.String(2048))
    group_id = db.Column(db.Integer, db.ForeignKey('task_group.id'), nullable=False)

    group = db.relationship('TaskGroup', back_populates='tasks')
    users = db.relationship('UserTask', back_populates='task')


class UserTask(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    task_id = db.Column(db.String(100), db.ForeignKey('task.id'), primary_key=True)
    status = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='tasks')
    task = db.relationship('Task', back_populates='users')


class TaskGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    tasks = db.relationship('Task', back_populates='group')
