#from app import create_app

#app = create_app(config_name='development')  # Use 'development' or 'production'

#if __name__ == '__main__':
#    app.run(debug=True)

from app import create_app
from waitress import serve

app = create_app(config_name='production')  # or 'default' if you're using that

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)


#source .venv/Scripts/activate