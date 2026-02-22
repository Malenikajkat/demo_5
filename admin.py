from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = db.session.execute(db.select(User).filter_by(username='admin')).scalar()
    if user:
        user.role = 'Admin'
        db.session.commit()
        print("✅ Пользователь теперь Admin")