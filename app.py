from config import * 
from api import *
from msgs import *
from web import *

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)
app.secret_key = secret_key_pw  # For login session in web console
app.config['JWT_SECRET_KEY'] = secret_key_jwt  # For storing UserID; used in specific retrieval of forms


# API for Application

if __name__ == '__main__':
    app.run(debug=True)