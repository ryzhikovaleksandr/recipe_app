from flask import Flask
from models import db, init_db
from routes import main_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret'

    # Инициализация базы данных
    db.init_app(app)

    # Регистрация blueprints
    app.register_blueprint(main_bp)

    # Создание таблиц и тестовых данных
    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
