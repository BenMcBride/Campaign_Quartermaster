from flask import Flask, session
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "little ricky"

bcrypt = Bcrypt(app)
DB = "campaign_quartermaster_schema"