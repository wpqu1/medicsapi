from flask import Flask, request, render_template, session, flash, make_response
from werkzeug.security import check_password_hash
from config import * 
from api import *
from msgs import *
import requests

web_bp = Blueprint('web', __name__)

# API for Web Console

@web_bp.route('/', methods=['GET', 'POST']) # Login Screen
def login():

    conn = getDb()
    cursor = conn.cursor()
    session['logged_in'] = False
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        cursor.execute("SELECT u.password FROM medics_users u JOIN medics_admins ma ON u.user_id = ma.user_id WHERE ma.username = ?", (username,))
        user_record = cursor.fetchone()

        if user_record:
            password_hash = user_record[0]
            if check_password_hash(password_hash, password):
                session['logged_in'] = True  # Set the session variables
                session['username'] = username
                flash('Logged in successfully', 'success')
                return render_template('dashboard.html', username=username)
            else:
                flash('Error: Invalid credentials.', 'danger')
                return render_template('hello.html')
        else:
            flash('Error: User not found.', 'danger')
            return render_template('hello.html')
    elif request.method == 'GET':
        # If it's a GET request, render the login page
        return render_template('hello.html')
    else:
        flash('Error: Method Not Allowed', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 405
        return response


@web_bp.route('/user_index', methods=['GET'])  # Main Menu
def user_index():

    try: 
        username = session['username']
        
        if not session.get('logged_in') and not username:  # Check if the user is logged in
            flash('Error: Insufficient Permissions.', 'danger')
            return render_template('hello.html')  # Redirect to login page if not logged in

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        params = {
            'record': 'user',
        }

        endpoint = '/get'
        url = f'{baseurl}{endpoint}'
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
        
            if response_data['status'] == 'success':
                user_data = response_data['data']  # List of user dictionaries
                if user_data:
                    flash('Retrieved data successfully', 'success')
                    return render_template('user_index.html', data=user_data)
                else:
                    flash('No user data available', 'danger')
                    return render_template('user_index.html', data=user_data)
            else:
                user_data = []
                flash('Failed to retrieve user data.', 'danger')
                return render_template('user_index.html', data=user_data)
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403
        return response


@web_bp.route('/form_index', methods=['GET'])
def form_index():

    try: 
        username = session['username']
    
        if not session.get('logged_in') and not username:  
            flash('Error: Insufficient Permissions.', 'danger')
            return render_template('hello.html') 
    
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        params = {
            'record': 'forms',
        }

        endpoint = '/get'
        url = f'{baseurl}{endpoint}'

        try:
            response = requests.get(url, params=params, headers=headers)
            response_data = response.json()

            if response_data['status'] == 'success':
                form_data = response_data['data']
                if form_data:
                    flash('Retrieved data successfully', 'success')
                    return render_template('form_index.html', data=form_data)
                else:
                    flash('An error occured! Check logs for details', 'danger')
                    return render_template('form_index.html')
            else:
                flash('No forms available', 'info')
                return render_template('form_index.html')
        
        except Exception as e:
            flash(f'An unexpected error occurred: {e}', 'danger')
            return render_template('form_index.html')
        
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403
        return response


@web_bp.route('/dashboard', methods=['GET']) # Main Menu
def dashboard():

    if not session.get('logged_in') and not session.get('username'):  # Check if the user is logged in
        flash('Error: Insufficient Permissions.', 'danger')
        return render_template('hello.html')  # Redirect to login page if not logged in
    
    try:
        username = session['username']
        return render_template('dashboard.html', username=username)
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403
        return response
    

@web_bp.route('/logout')
def logout():
    try: 
        if session.get('logged_in') and session.get('username'):
            session['logged_in'] = False
            session.clear()
            flash('You have been logged out.', 'info')
            return render_template('hello.html')
        else:
            flash('Error: You are not logged in.', 'danger')
            response = make_response(render_template('hello.html'))
            response.status_code = 403
            return response
    except Exception as e:
        flash('Error: Method Not Allowed.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 405
        return response


@web_bp.route('/record_register', methods=['GET', 'POST']) # /add
def record_register():

    try: 
        username1 = session['username']

        if request.method == 'GET':

            if not session.get('logged_in') and not session.get('username'):
                flash('Error: Insufficient Permissions.', 'danger')
                return render_template('hello.html')          # Redirect to login page if not logged in
            else:
                return render_template('admin_register.html') # Otherwise, go to desired page
            
        elif request.method == 'POST':

            '''Form data input from html'''
            email = request.form['email']                           # Important
            password = request.form['password']                     # Important
            firstname = request.form['firstname']                   # Important
            lastname = request.form['lastname']                     # Important
            birthdate = request.form['birthdate']                   # Important
            contact = request.form['contact']                       # Important
            username = request.form['username']                     # Admins Only
            student_number = request.form['student_number']         # Students Only
            course = request.form['course']                         # Students Only
            section = request.form['section']                       # Students Only
            employee_number = request.form['employee_number']       # Employees Only
            position = request.form['position']                     # Employees Only

            headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

            params = { 
            'record': request.form['record'],                       # Critical
            'type': request.form['type']                            # Critical
            }

            endpoint = '/add'
            url = f'{baseurl}{endpoint}'

            data = {
                'email': email,
                'password': password,
                'firstname': firstname,
                'lastname': lastname,
                'birthdate': birthdate,
                'contact': contact,
                'username': username
                }
        
            ''' Logic that checks query params for user_type'''
            if params['type'] == "admin":
                data['username'] = username 
            elif params['type'] == "student":
                data['student_number'] = student_number, 
                data['course'] = course, 
                data['section'] = section 
            elif params['type'] == "employee":
                data['position'] = position,
                data['employee_number'] = employee_number
            else:
                flash('Invalid user type in query parameters', 'danger')
                return render_template('admin_register.html')

            try:
                response = requests.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Process the response if needed
                if response.status_code == 201:
                    flash('User registered successfully.', 'success')
                    return render_template('dashboard.html', username=username1)
                else:
                    flash('Failed to register user.', 'danger')
                    return render_template('admin_register.html')

            except Exception as e:
                flash(f'An unexpected error occurred: {e}', 'danger')
                return render_template('admin_register.html')
            
        else:
            flash('Method not allowed', 'danger')
            return render_template('admin_register.html')
        
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403
        return response


@web_bp.route('/record_edit', methods=['GET', 'PUT']) # /edit
def record_edit():

    try:
        username1 = session['username']

        if request.method == 'GET':
            if not session.get('logged_in') and not session.get('username'):
                flash('Error: Insufficient Permissions.', 'danger')
                return render_template('hello.html')  # Redirect to login page if not logged in
            else:
                return render_template('admin_edit.html')

        elif request.method == 'PUT':
            '''Form data input from html'''
            email = request.form['email']
            password = request.form['password']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            birthdate = request.form['birthdate']
            contact = request.form['contact']
            username = request.form['username']
            student_number = request.form['student_number']
            course = request.form['course']
            section = request.form['section']
            employee_number = request.form['employee_number']
            position = request.form['position']

            headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

            '''Commented out to test if request.form can be used to pass data to params''' 
            params = { 
            'record': request.form['record'],
            'type': request.form['type']
            }

            endpoint = '/edit'
            url = f'{baseurl}{endpoint}'

            data = {
            'email': email,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'birthdate': birthdate,
            'contact': contact,
            'username': username
            }
        
            ''' Logic that checks query params for user_type'''
            if params['type'] == "admin":
                data['username'] = username 
            elif params['type'] == "student":
                data['student_number'] = student_number, 
                data['course'] = course, 
                data['section'] = section, 
            elif params['type'] == "employee":
                data['position'] = position
                data['employee_number'] = employee_number
            else:
                flash('Invalid user type in query parameters', 'danger')
                return render_template('admin_edit.html')

            try:

                headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
                }

                '''Commented out to test if request.form can be used to pass data to params''' 
                params = { 
                'id': request.form['id'],
                'type': request.form['type']
                }

                response = requests.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Process the response if needed
                if response.status_code == 201:
                    flash('User info edited successfully.', 'success')
                    return render_template('dashboard.html', username=username1)
                else:
                    flash('Failed to edit user info.', 'danger')
                    return render_template('admin_edit.html')

            except Exception as e:
                flash(f'An unexpected error occurred: {e}', 'danger')
                return render_template('admin_edit.html')
        else:
            flash('Error: Method Not Allowed.', 'danger')
            response = make_response(render_template('hello.html'))
            response.status_code = 405
            return response
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403 
        return response


@web_bp.route('/record_delete', methods=['GET', 'DELETE']) # /edit
def record_delete():

    try:
        username = session['username']

        if request.method == 'GET':
            if not session.get('logged_in') and not session.get('username'):
                flash('Error: Insufficient Permissions.', 'danger')
                return render_template('hello.html')  # Redirect to login page if not logged in
            else:
                return render_template('admin_delete.html')

        elif request.method == 'DELETE':

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
                }

            '''Commented out to test if request.form can be used to pass data to params''' 
            data = { 
                'id': request.form['id'],
                'type': request.form['type']
                }
        
            params = {
                'record': request.form['record']
            }

            endpoint = '/delete'
            url = f'{baseurl}{endpoint}'
        
            try:
                response = requests.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Process the response if needed
                if response.status_code == 201:
                    flash('User deleted successfully.', 'success')
                    return render_template('dashboard.html', username=username)
                else:
                    flash('Failed to delete user.', 'danger')
                    return render_template('admin_delete.html')

            except Exception as e:
                flash(f'An unexpected error occurred: {e}', 'danger')
                return render_template('admin_delete.html')
        else:
            flash('Error: Method Not Allowed.', 'danger')
            response = make_response(render_template('hello.html'))
            response.status_code = 405
            return response
    except Exception as e:
        flash('Error: Insufficient Permissions.', 'danger')
        response = make_response(render_template('hello.html'))
        response.status_code = 403
        return response