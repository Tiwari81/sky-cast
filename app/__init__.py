from flask import Flask, render_template
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    
    CORS(app)

    # Register Blueprints
    from app.routes.weather_routes import weather_bp
    from app.routes.location_routes import location_bp
    from app.routes.history_routes import history_bp
    from app.routes.favorites_routes import favorites_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(weather_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
