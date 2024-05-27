import json
from api import app, db
from api.models import User, Task, TaskGroup

with app.app_context():
    db.create_all()

    # Создаем админа
    admin = User(email='admin@admin.ru', name='Админов Админ Админович', password='$2b$12$fmxCuMWmm09hjbzLd3hIFeFWUhEaB9xD5dbK.mAOpeEYBh8o.iIF.', role='admin')
    db.session.add(admin)
    db.session.commit()

    # Добавляем дефолтный набор задач
    with open('data/groups_with_tasks.json', 'r') as f:
        groups = json.load(f)

        for group in groups:
            new_group = TaskGroup(id=group['id'], name=group['name'])
            db.session.add(new_group)
            db.session.commit()

            for task in group['tasks']:
                new_task = Task(id=task['id'], name=task['name'], description=task['description'], group_id=group['id'], tests=task['tests'])
                db.session.add(new_task)
                db.session.commit()
