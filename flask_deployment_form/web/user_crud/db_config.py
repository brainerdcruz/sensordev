from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'senslope'
app.config['MYSQL_DATABASE_DB'] = 'senslopedb'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'#'192.168.150.77'
mysql.init_app(app)