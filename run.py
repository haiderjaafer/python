from app import create_app

app = create_app(config_name='development')  # Use 'development' or 'production'

if __name__ == '__main__':
    app.run(debug=True)