# entry file to the application
from flaskr import create_app
from os import environ
# creating the app with configuration durrived from FLASK_CONFIG environment variable, or fall back to development.
config = environ.get('FLASK_CONFIG') or 'development'
app = create_app(config)

# finally, run the app
if __name__ == "__main__":
    app.run()
