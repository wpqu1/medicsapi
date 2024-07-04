import mariadb

# Configuration File

secret_key_pw = 'bcdd57ce2983c027d22391629df9e875ccd41ce75b64a5a361157ba9a6aade86'
secret_key_jwt = 'ccd41ce75b64a5a361157ba9a6aade86bcdd57ce2983c027d22391629df9e875'
pwformat = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$'
emformat = r"[^@]+@iskolarngbayan\.pup\.edu\.ph$"
baseurl = 'http://localhost:5000'

def getDb():
    connection = mariadb.connect (
    host="localhost",
    user="root",
    password="",
    database="medics",
    )
    return connection

