from flask import Flask
from app.database.connection import DatabaseConnection

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration
    if config_name == 'development':
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        raise ValueError(f"Invalid configuration name: {config_name}")

    # Initialize database connection
    DatabaseConnection.initialize(app.config['DATABASE_URI'])

    # Register blueprints
    from app.routes.order_routes import bp as order_bp
    from app.routes.committee_routes import bp as committee_bp
    from app.routes.department_routes import bp as department_bp
    from app.routes.estimator_routes import bp as estimator_bp

    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(committee_bp, url_prefix='/api/committees')
    app.register_blueprint(department_bp, url_prefix='/api/departments')
    app.register_blueprint(estimator_bp, url_prefix='/api/estimators')

    return app