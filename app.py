from flask import Flask
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///chirphub-db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "qwhdu&*UJdwqdqw"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/test', methods=['GET', 'POST'])
def testing_api():
    return 'test'










if __name__ == '__main__':
    app.run(debug=True)