import json
from api import app, db
from api.models import User, Task, TaskGroup

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Создаем админа
        if User.query.count() == 0:
            admin = User(email='admin@admin.ru', name='Админов Админ Админович', password='$2b$12$fmxCuMWmm09hjbzLd3hIFeFWUhEaB9xD5dbK.mAOpeEYBh8o.iIF.', role='admin')
            db.session.add(admin)
            db.session.commit()

    app.run(host='0.0.0.0', port=5050)
