from flask import Flask
from app.database.connection import DatabaseConnection
from flask_cors import CORS

def create_app(config_name='production'):
    app = Flask(__name__)
    #app.url_map.strict_slashes = False  # Critical!
    # Allow requests from Next.js dev server
    #CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    # Dynamic CORS configuration

    # CORS Configuration
    CORS(
    app,
    origins=["http://localhost:3000"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)



 
    if config_name == 'development':
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        # Ensure all required configs are set
        app.config['PDF_BASE_PATH'] = DevelopmentConfig.PDF_BASE_PATH
    elif config_name == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
        app.config['PDF_BASE_PATH'] = ProductionConfig.PDF_BASE_PATH
    else:
        raise ValueError(f"Invalid configuration name: {config_name}")

    # Initialize database connection
    DatabaseConnection.initialize(app.config['DATABASE_URI'])
    print(f" app file.... {__name__}")
    print(f" app file app.... {app}")
    # Register blueprints
    from app.routes.order_routes import bp as order_bp
    from app.routes.committee_routes import bp as committee_bp
    from app.routes.department_routes import bp as department_bp
    from app.routes.estimator_routes import bp as estimator_bp
    from app.routes.pdf_routes import bp as pdf_bp

    print(f" app file.... {committee_bp}")
    
    app.register_blueprint(order_bp)
    app.register_blueprint(committee_bp, url_prefix='/api/committees')
    app.register_blueprint(department_bp, url_prefix='/api/departments')
    app.register_blueprint(estimator_bp, url_prefix='/api/estimators')
    app.register_blueprint(pdf_bp)


    return app