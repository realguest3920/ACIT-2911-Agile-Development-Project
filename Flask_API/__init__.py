from app import app as web_app
from app.routes import api_bp


def create_app():
    if "marketplace" not in web_app.blueprints:
        web_app.register_blueprint(api_bp)
    return web_app