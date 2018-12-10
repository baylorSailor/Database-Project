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
from flask import Flask, flash,redirect,session,abort, request, render_template, make_response, url_for
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
from flask_user import login_required, user_manager, user_mixin, SQLAlchemyAdapter
from functools import wraps

import json
import os

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
ACCESS = {
    'guest': 0,
    'user': 1,
    'admin': 2
}

class User():
    def __init__(self, username, password, access=ACCESS['user']):
        self.username = username
        self.password = password
        self.access = access

    def is_admin(self):
        return self.access == ACCESS['admin']

    def allowed(self, access_level):
        return self.access >= access_level

@app.route('/login')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'), 200, headers)


@app.route('/HandleLogin', methods=['POST'])
def do_login():
    password = request.form['password']
    username = request.form['username']

    cursor = conn.cursor()
    validUser = False
    query = "select username from `databasegroupproject`.`user`"
    cursor.execute(query)
    result = cursor.fetchall()
    for row in result:
        for col in row:
            if col == username:
                validUser = True
    print(validUser)
    query = "select username from `databasegroupproject`.`admin`"
    cursor.execute(query)
    result = cursor.fetchall()
    for row in result:
        for col in row:
            if col == username:
                validUser = True

    print(validUser)
    if validUser:
        query = "select password from `databasegroupproject`.`user` where username=%s"
        cursor.execute(query, username)
        result = cursor.fetchall()
        tempPass1 = ''
        tempPass2 = ''
        for row in result:
            for col in row:
                tempPass1 = col
        query = "select password from `databasegroupproject`.`admin` where username=%s"
        cursor.execute(query, username)
        result = cursor.fetchall()
        for row2 in result:
            for col2 in row2:
                tempPass2 = col2
        if password == tempPass1:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'student'
            flash('Welcome back, '+username)
        elif password == tempPass2:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'admin'
            flash('Welcome back administrator' + username)
        else:
            flash('wrong password!', 'danger')
    else:
        flash('wrong username!', 'danger')
    return home()

@app.route("/logout")
def logout():
    flash('logout successful', 'success')
    session['logged_in'] = False
    return home()
# class Login(Resource):
#     def home(self):
#         if not session.get('logged_in'):
#             return render_template('login.html')
#         else:
#             headers = {'Content-Type': 'text/html'}
#             return make_response(render_template('index.html'), 200, headers)
#
# class HandleLogin(Resource):
#     def do_admin_login(self):
#         if request.form['password']: == 'password' and request.form ['']
#             return render_template('login.html')
#         else:
#             headers = {'Content-Type': 'text/html'}
#             return make_response(render_template('index.html'), 200, headers)


def requires_roles(*roles):
    print('checking role')
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            print(session)
            if not session.get('logged_in'):
                return redirect(url_for('home'))
            elif session['role'] in roles:
                return f(*args, **kwargs)
            else:
                flash('not allowed', 'danger')
                return redirect(url_for('HelloWorld'))
        return wrapped
    return wrapper
# this class is a simple helloWorld response to a HTTP GET request or an echo response to a POST request.
class HelloWorld(Resource):
    #    @app.route('/')

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html'), 200, headers)

    def post(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('success.html'), 200, headers)
    # def home(self):
    #     if not session.get('logged_in'):
    #         return render_template('login.html')
    #     else:
    #         headers = {'Content-Type': 'text/html'}
    #         return make_response(render_template('index.html'), 200, headers)
    #
    # def post(self):
    #     headers = {'Content-Type': 'text/html'}
    #     return make_response(render_template('success.html'), 200, headers)


# This class will take a GET request that also contains a key value called 'num'.
# it will take the number that is paired with 'num', multiply it by 10 and return it to the front-end service.
# CURRENTLY DOES NOT WORK



class Multi(Resource):
    def get(self, num):
        return {'result': num * 10}


# This class will take any get request. Once a request is received ti will make a query to a MySQL schema,
# and it will return the tuples to the sender in JSON format.
# NOTE: there were some issues with the conversion of a datetype to Json, so we can handle that later.
class TestSQL(Resource):
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

class RegisterStudent(Resource):
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


class StudentRegister(Resource):
    def get(self):
        return {'about': 'Hello World'}

    def post(self):
        cursor = conn.cursor()
        first = request.form["First"]
        last = request.form["Last"]
        middle = request.form["Middle"]
        suffix = request.form["Suffix"]
        preffered = request.form["Preffered"]
        address = request.form["Address"]
        city = request.form["City"]
        state = request.form["State"]
        zipcode = request.form["Zip"]
        birth = request.form["Birthdate"]
        if request.form["Gender"] == "M":
            gender = 0
        else:
            gender = 1
        race = request.form["Race"]
        schooltype = request.form["schoolType"]
        district = request.form["District"]
        schoolname = request.form["HighSchool"]
        graddate = request.form["GradDate"]
        email = request.form["Email"]
        phone = request.form["Phone"]
        siblingusername = request.form["SiblingUsername"]

        query = "INSERT INTO `databasegroupproject`.`applications` values (\'%s\', \'%s\', \'%s\', \'%s\',\'%s\'," \
                "\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')"
        values = (first, last, middle, suffix, preffered, address, city, state, zipcode, birth, str(gender), race, email,
                  phone, schooltype, district, schoolname, graddate, siblingusername)
        query = query % values
        cursor.execute(query)
        conn.commit()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('success.html'), 200, headers)


class StudentsParents(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('StudentsParents.html'), 200, headers)


class StudentApply(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('apply.html'), 200, headers)


class Staff(Resource):
    @requires_roles('admin')
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('staff.html'), 200, headers)

class HandleStaff(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        student = request.form["studentUsername"]
        year = request.form["Year"]
        grade = request.form["grade"]
        status = request.form["Status"]
        funded = request.form["Funded"]
        grant = request.form["Grant"]
        firstmentor = request.form["First"]
        lastmentor = request.form["Last"]
        siblinguser = request.form["SiblingUsername"]
        disability = request.form["Disabilities"]
        health = request.form["Health"]
        gifted = request.form["gt"]
        if gifted == "No":
            gifted = 0
        else:
            gifted = 1
        misc = request.form["description"]
        ell = request.form["English"]
        if ell == "No":
            ell = 0
        else:
            ell = 1
        query = "select idStudent from `databasegroupproject`.`user` where username=%s"
        cursor = conn.cursor()
        cursor.execute(query, student)
        result = cursor.fetchall()
        for row in result:
            for col in row:
                values = (str(col), '', '', '', '', '', '', '', '', '', '1000-01-01', '0', '', '', '', gifted, year,
                          grade,
                          status, ell, misc, year, grade, status, ell, misc, gifted)
                query = "Insert into `databasegroupproject`.`student` values (\'%s\', \'%s\', \'%s\',\'%s\',\'%s\'," \
                        "\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\'," \
                        "\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\') on duplicate key update " \
                        "YearAccepted=" \
                        "\'%s\', GradeWhenAccepted=\'%s\', " \
                        "Status=\'%s\', ELL=\'%s\', misc=\'%s\',GTProgram=\'%s\'"
                query = query % values
                cursor.execute(query)

                if funded == "no":
                    nch = "no"
                    funded = 0
                else:
                    if status == "Graduated":
                        nch = "yes"
                    else:
                        nch = "no"
                    funded = 1
                query = "Insert into `databasegroupproject`.`funding` values (\'%s\',\'%s\',\'%s\',\'%s\') " \
                        "on duplicate key update Funding=\'%s\', grantname=\'%s\', nationalclearinghouseinfo=\'%s\'"
                values = (str(col), funded, grant, nch, funded, grant, nch)
                query = query % values
                cursor.execute(query)

                mentor = firstmentor + " " + lastmentor
                query = "insert into `databasegroupproject`.`mentor` values (\'%s\',\'%s\') " \
                        "on duplicate key update mentorname=\'%s\'"
                values = (str(col), mentor, mentor)
                query = query % values
                cursor.execute(query)

                query = "select idStudent from `databasegroupproject`.`user` where username=%s"
                cursor.execute(query, siblinguser)
                result = cursor.fetchall()
                for newR in result:
                    for newC in newR:
                        query = "insert into `databasegroupproject`.`sibling` values (\'%s\',\'%s\') " \
                                "on duplicate key update idSibling = \'%s\'"
                        values = (str(col), str(newC), str(newC))
                        query = query % values
                        cursor.execute(query)

                query = "insert into `databasegroupproject`.`health condition` values (\'%s\',\'%s\') " \
                        "on duplicate key update type=\'%s\'"
                values = (str(col), health, health)
                query = query % values
                cursor.execute(query)

                query = "insert into `databasegroupproject`.`disability` values (\'%s\',\'%s\') " \
                        "on duplicate key update type=\'%s\'"
                values = (str(col), disability, disability)
                query = query % values
                cursor.execute(query)
                conn.commit()
                return make_response(render_template('success.html'), 200, headers)
        return make_response(render_template('staff.html'), 200, headers)



class StudentSignIn(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('studentSignIn.html'), 200, headers)


class HandleStudentSignIn(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        username = request.form["username"]
        password = request.form["password"]
        query = "Select password from `databasegroupproject`.`user` where username=%s"
        cursor = conn.cursor()
        cursor.execute(query, username)
        result = cursor.fetchall()
        for row in result:
            for column in row:
                if column == password:
                    app.config['MYSQL_DATABASE_USER'] = 'User'
                    app.config['MYSQL_DATABASE_PASSWORD'] = 'UserPassword'
                    return make_response(render_template('success.html'), 200, headers)
        return make_response(render_template('studentSignIn.html'), 200, headers)


class StaffSignIn(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('staffSignIn.html'), 200, headers)


class HandleStaffSignIn(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        username = request.form["username"]
        password = request.form["password"]
        query = "Select password from `databasegroupproject`.`admin` where username=%s"
        cursor = conn.cursor()
        cursor.execute(query, username)
        result = cursor.fetchall()
        for row in result:
            for column in row:
                if column == password:
                    app.config['MYSQL_DATABASE_USER'] = 'Admin'
                    app.config['MYSQL_DATABASE_PASSWORD'] = 'AdminPassword'
                    return make_response(render_template('success.html'), 200, headers)

        return make_response(render_template('staffSignIn.html'), 200, headers)


class staffNewUser(Resource):
    @requires_roles('admin')
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('staffCreateUser.html'), 200, headers)
class handleStaffNewUser(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        username = request.form["username"]
        password = request.form["password"]
        roll = request.form["userRole"]

        if roll == "Admin":
            query = "select username from `databasegroupproject`.`admin` where username=%s"
            cursor = conn.cursor()
            cursor.execute(query, username)
            result = cursor.fetchall()
            for row in result:
                for column in row:
                    if column == username:
                        return make_response(render_template('staffCreateUser.html'), 200, headers)
            query = "Insert into `databasegroupproject`.`admin` Values (%s,%s)"
            values = (username, password)
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
        else:
            query = "select username from `databasegroupproject`.`user` where username=%s"
            cursor = conn.cursor()
            cursor.execute(query, username)
            result = cursor.fetchall()
            for row in result:
                for column in row:
                    if column == username:
                        return make_response(render_template('staffCreateUser.html'), 200, headers)
            query = "Insert into `databasegroupproject`.`user` (username, password) Values (%s,%s)"
            values = (username, password)
            cursor.execute(query, values)
            conn.commit()
        return make_response(render_template('success.html'), 200, headers)

class showClasses(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('classes.html'), 200, headers)

class createClass(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('createClass.html'), 200, headers)

class handleCreateClass(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        print(request.form)
        level = request.form["level"]
        name = request.form["className"]
        capacity = request.form["capacity"]
        room = request.form["room"]
        instructor = request.form["instructor"]
        cost = request.form["cost"]
        query = "select * from `databasegroupproject`.`classes`"
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            print(row)
        query = "insert into `databasegroupproject`.`classes` (level, name, capacity, room, instructor, cost) values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\'," \
                " \'%s\')"
        values = (level, name, capacity, room, instructor, cost)
        query = query % values
        print(query)
        cursor.execute(query)
        conn.commit()
        return make_response(render_template('success.html'), 200, headers)

class staffIndex(Resource):
    @requires_roles('admin')
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('staffIndex.html'), 200, headers)

class createSession(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('createSession.html'), 200, headers)

class handleCreateSession(Resource):
    def post(self):
        headers = {'Content-Type': 'text/html'}
        print(request.form)
        return make_response(render_template('success.html'), 200, headers)
# These function calls simply establish endpoints that will be associated with the functions defined above
# an endpoint is simply an url where a client can reach an API to make requests.
# I'd recommend using Postman to test these functions. Good Luck!

# when you run thi program, the consol should show what address it is runnin off of.
# add the following paths to the address to access it's different functions.
# eg:  http://127.0.0.1:5000/testSQL
#      http://127.0.0.1:5000/
#      http://127.0.0.1:5000/register/student


api.add_resource(HelloWorld, '/')  # a Get request to the root will warrant a hello world response
api.add_resource(Multi, '/multi')
api.add_resource(StudentsParents, '/StudentsParents.html')
api.add_resource(TestSQL, '/testSQL')
api.add_resource(StudentApply, '/apply')
api.add_resource(Staff, '/staff')
api.add_resource(StudentRegister, '/register/student')
api.add_resource(StudentSignIn, '/studentSignIn')
api.add_resource(HandleStudentSignIn, '/handleStudentSignIn')
api.add_resource(StaffSignIn, '/staffSignIn')
api.add_resource(HandleStaffSignIn, '/handleStaffSignIn')
api.add_resource(staffNewUser, '/staffNewUser')
api.add_resource(handleStaffNewUser, '/handleStaffNewUser')
api.add_resource(HandleStaff, '/handleStaff')
api.add_resource(showClasses, '/showClasses')
api.add_resource(createClass, '/createClass')
api.add_resource(handleCreateClass, '/handleCreateClass')
api.add_resource(staffIndex, '/staffIndex')
api.add_resource(createSession, '/createSession')
api.add_resource(handleCreateSession, '/handleCreateSession')
#this will finally run our server once all other aspects of it hav ebeen created.


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
