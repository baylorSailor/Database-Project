# Author: Cedric Boston
# File Name: RestAPI
# File Description: This program will create a simple restfullAPI that provides examples
# of some of Flask's capabilities. These example include handling multiple request types at a single endpoint,
# requesting MySQL data and sending the json formatted tuples to a front-end service, and parsing data send by the
# front end service into variables for possible insertion into a table.
# necessary libraries:
    # Flask-RESTFUL
    # Flask-MySQL
    # Flask
    # whatever version of python MySQL that is necessary for your operating system.
        # refer to this video: https://www.youtube.com/watch?v=x7SwgcpACng&t=
# These are the imports that are needed for this program to work.
# The Flask and request imports are included to handle whatever http requests are sent to our server
# The flask_restful imports help with streamlining the api creation process so it is much more managable
#   trying to code this without using the Flask_restful tools could be a problem with medium/large programs
# The JSON import is what will handle converting the mysql tuple data into an easier to handle JSON format.
from flask import Flask, request, render_template, make_response
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
import json

# these lines are establish the setup for the API.
# The Flask() function call assigns the name "main" to this instance
# The Api() function call handles the actual server setup for our new instance
# The MySQL function simply gives us a way to interact with a MySQL server (like in program 1)

app = Flask(__name__)
api = Api(app)
mysql = MySQL()


# MySQL configurations
# for some reason, the port is not needed. So I assume it
#   searches through all of them until it finds the right one

# I've changed these values so be easily discernible.
# Be sure to change them into values that work for you.
app.config['MYSQL_DATABASE_USER'] = 'Master'
app.config['MYSQL_DATABASE_PASSWORD'] = '91097TheMasterPassword1997'
app.config['MYSQL_DATABASE_DB'] = 'databasegroupproject'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# attempting the mysql connection with our Flask app's mysql configurations.
mysql.init_app(app)
conn = mysql.connect()

# this class is a simple helloWorld response to a HTTP GET request or an echo response to a POST request.
class HelloWorld(Resource):
#    @app.route('/')
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'), 200, headers)

    def post(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('success.html'), 200, headers)

# This class will take a GET request that also contains a key value called 'num'.
# it will take the number that is paired with 'num', multiply it by 10 and return it to the front-end service.
# CURRENTLY DOES NOT WORK
class Multi(Resource):
    def get(self, num):
        return {'result': num*10}

# This class will take any get request. Once a request is received ti will make a query to a MySQL schema,
    # and it will return the tuples to the sender in JSON format.
# NOTE: there were some issues with the conversion of a datetype to Json, so we can handle that later.
class testSQL(Resource):
    def get(self):
        try:
            # creating a mysql cursor form our conn variable that was created earlier
            cursor = conn.cursor()
            cursor.execute('''SELECT ParameterName FROM parameterstypes''')
            row_headers = [x[0] for x in cursor.description]  # this will extract row headers
            rv = cursor.fetchall()
            json_data = []
            for result in rv:
                # this will append the json formatted data to our json_data object
                json_data.append(dict(zip(row_headers, result)))
            return json.dumps(json_data)
        except Exception as e:
            return {'error': str(e)}

# this is just a basic parsing example. if you make a POST request here it will look for the keywords
    # that should be associated with the request. the POST request will need to have two key-value pairs:
    # email: <emailaddress>
    # password: <password>
    # if either one of these is not found, it will return an error.

class registerStudent(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email address to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            args = parser.parse_args()

            _userEmail = args['email']
            _userPassword = args['password']

            return {'Email': args['email'], 'Password': args['password']}

        except Exception as e:
            return {'error': str(e)}

class studentRegister(Resource):
    def get(self):
        print(request.get_json())
        return{'about':'Hello World'}

    def post(self):
        print(request.form)
        print("received data")
        print(request.form["Last"])
        print(request.get_json(force=True))
        print()
        print(request.get_data())
        cursor = conn.cursor()
        query = "INSERT INTO student (FirstName, LastName, MiddleInitial, Suffix, NickName, Address, City, State, ZIP, Birthdate, Gender, Race, Email, Phone Number, GTProgram, YearAccepted, GradeWhenAccepted, Status, ELL, MISC) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (request.form["First"], request.form["Last"], request.form["Middle"], request.form["Suffix"], request.form["Preffered"], request.form["Address"], request.form["City"], request.form["State"], request.form["Zip"], request.form["Birthdate"], request.form["Gender"], request.form["Race"], request.form["Email"], request.form["Phone"], 'N', '2018', '72', 'yes', '10', 'Hello')
        print(query)
        print(values)
        cursor.execute(query, values)
        some_json=request.get_json()
        return {request.form}, 200

class StudentsParents(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('StudentsParents.html'), 200, headers)
class studentApply(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('apply.html'), 200, headers)

class staff(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('staff.html'), 200, headers)
# These function calls simply establish endpoints that will be associated with the functions defined above
# an endpoint is simply an url where a client can reach an API to make requests.
# I'd recommend using Postman to test these functions. Good Luck!

# when you run thi program, the consol should show what address it is runnin off of.
    # add the following paths to the address to access it's different functions.
# eg:  http://127.0.0.1:5000/testSQL
#      http://127.0.0.1:5000/
#      http://127.0.0.1:5000/register/student

api.add_resource(HelloWorld, '/') # a Get request to the root will warrant a hello world response
api.add_resource(Multi, '/multi')
api.add_resource(StudentsParents, '/StudentsParents.html')
api.add_resource(testSQL, '/testSQL')
api.add_resource(studentApply, '/apply')
api.add_resource(staff, '/staff')
api.add_resource(studentRegister, '/register/student')

#this will finally run our server once all other aspects of it hav ebeen created.
if __name__ == '__main__':
    app.run(debug=True)