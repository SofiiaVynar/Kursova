from flask import Flask
from flask_login import LoginManager

from api.transport_api import vehicle_bp, driver_bp, trip_bp, maintenance_bp, expense_bp, report_bp
from api.web_routes import web_bp, auth_bp
from config import Config
from domain.models import User
from extensions import db, migrate

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(vehicle_bp, url_prefix='/api/vehicles')
    app.register_blueprint(driver_bp, url_prefix='/api/drivers')
    app.register_blueprint(trip_bp, url_prefix='/api/trips')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')
    app.register_blueprint(report_bp, url_prefix='/api/reports')

    # Реєстрація веб-Blueprint
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
