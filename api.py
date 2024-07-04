import re
from datetime import datetime
from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from config import *
from msgs import *

api_bp = Blueprint('api', __name__)

# API for MEDICS App
# Query parameters: record (user/forms) & type (user/employee/admin) & id (user_id)

@api_bp.route('/get', methods=['GET'])
def httpGet():
    try:
        conn = getDb()
        cursor = conn.cursor()
        record = request.args.get("record") # user or forms

        if record == "user":
            user_id = request.args.get("id")
            user_type = request.args.get("type")

            query = """
            SELECT 
                u.user_id, u.user_type, u.email, u.firstname, u.lastname, u.birthdate, u.contact,
                u.date_joined, s.student_number, s.course, s.section,
                e.employee_number, e.employee_type, e.position
            FROM 
                medics_users u
            LEFT JOIN 
                medics_students s ON u.user_id = s.user_id
            LEFT JOIN 
                medics_employees e ON u.user_id = e.user_id
            """
            params = []

            if user_id and user_type:
                query += " WHERE u.user_id = ? AND u.user_type = ?"
                params = [user_id, user_type]
            elif user_id:
                query += " WHERE u.user_id = ?"
                params = [user_id]
            elif user_type:
                query += " WHERE u.user_type = ?"
                params = [user_type]

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            # results = [dict(zip(columns, row)) for row in rows] // Artifact code, don't remove
            results = []
            for row in rows:
                row_dict = {columns[i]: value for i, value in enumerate(row) if value is not None}
                results.append(row_dict)

            if results:
                return Messages.json_success_response(results), 200
            else:
                return Messages.json_fail_response("No matching users found."), 404
        
        elif record == "forms":
            form_id = request.args.get("id")
            form_type = request.args.get("type") # appointment / emergency / notification

            query = """ 
            SELECT * FROM medics_forms
            """
            params = []

            if form_id and form_type:
                query += " WHERE form_id = ? AND form_type = ?"
                params = [form_id, form_type]
            elif form_id:
                query += " WHERE form_id = ?"
                params = [form_id]
            elif form_type:
                query += " WHERE form_type = ?"
                params = [form_type]

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            results = []

            for row in rows:
                row_dict = {columns[i]: value for i, value in enumerate(row) if value is not None}
                results.append(row_dict)

            if results:
                return Messages.json_success_response(results), 200
            else:
                return Messages.json_fail_response("No matching forms found."), 404
        
        else:
            return Messages.json_fail_response("Invalid record type"), 400
    
    except Exception as e:
        return Messages.json_fail_response(str(e)), 500
    
    finally:
        conn.close()


@api_bp.route('/add', methods=['POST'])
def httpPost():
    try:
        conn = getDb()
        cursor = conn.cursor()
        record = request.args.get("record") # user or forms
        current_date = datetime.now()
        date_joined = current_date.strftime('%Y-%m-%d %H:%M:%S')

        if record == "user":
            user_type = request.args.get("type") # admin / student / employee
            data = request.get_json()

            if not data:
                return Messages.json_fail_response("Missing JSON data."), 400
        
            if not re.match(emformat, data.get('email', '')):
                return Messages.json_fail_response("Invalid email domain. Please use your PUP Webmail."), 400
        
            if not re.match(pwformat, data.get('password', '')):
                return Messages.json_fail_response("Invalid password combination. Please use letters, numbers, and symbols."), 400
        
            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

            cursor.execute("""
                INSERT INTO medics_users (user_type, email, password, firstname, lastname, birthdate, contact, date_joined)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_type, data['email'], hashed_password, data['firstname'], data['lastname'], data['birthdate'], data['contact'], date_joined))

            user_id = cursor.lastrowid
        
            if user_type == "student":
                cursor.execute("""
                    INSERT INTO medics_students (student_number, user_id, course, section)
                    VALUES (?, ?, ?, ?)
                    """, (data['student_number'], user_id, data['course'], data['section']))
        
            elif user_type == "employee":
                employee_type = data['employee_type']
                cursor.execute("""
                    INSERT INTO medics_employees (employee_number, user_id, employee_type, position)
                    VALUES (?, ?, ?, ?)
                    """, (data['employee_number'], user_id, employee_type, data['position']))
            
            elif user_type == "admin":
                cursor.execute("""
                    INSERT INTO medics_admins (user_id, username)
                    VALUES (?, ?)
                    """, (user_id, data['username']))
            else:
                return Messages.json_fail_response("Invalid user type."), 400
            conn.commit()
            return Messages.json_success_response(data), 201
        
        elif record == "forms":
            form_type = request.args.get("type") # appointment / emergency / notification
            data = request.get_json()
            status = "pending"
            current_date = datetime.now()
            date_created = current_date.strftime('%Y-%m-%d %H:%M:%S')

            if not data:
                return Messages.json_fail_response("Missing JSON data."), 400
        
            if form_type in ["appointment", "emergency", "notification"]:
                cursor.execute("""
                INSERT INTO medics_forms (form_type, user_id, status, patient_name, date_created, created_by, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (form_type, data['user_id'], status, data['patient_name'], date_created, data['created_by'], data['remarks']))
            else:
                return Messages.json_fail_response("Invalid form type"), 400
            conn.commit()    
            return Messages.json_success_response(data), 201
        
        else:
            return Messages.json_fail_response("Invalid record type"), 400

    except Exception as e:
        return Messages.json_fail_response(str(e)), 500

    finally:
        conn.close()


@api_bp.route('/edit', methods=['PUT'])
def httpPut():
    try:
        conn = getDb()
        cursor = conn.cursor()
        record = request.args.get("record") # user or forms 

        if record == "forms":
            updated_user_data = {}
            form_id = request.args.get("id")
            if 'status' in request.json:
                updated_user_data['status'] = request.json['status']
            if 'patient_name' in request.json:
                updated_user_data['patient_name'] = request.json['patient_name']
            if 'remarks' in request.json:
                updated_user_data['remarks'] = request.json['remarks']
            if 'created_by' in request.json:
                updated_user_data['created_by'] = request.json['created_by']
            if not updated_user_data:
                return Messages.json_fail_response("No data passed"), 400

            set_clause = ', '.join([f"{key} = ?" for key in updated_user_data.keys()])
            query = f"UPDATE medics_forms SET {set_clause} WHERE form_id = ?"
            params = list(updated_user_data.values()) + [form_id]
            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                return Messages.json_fail_response("User ID not found"), 404
            else:
                return Messages.json_success_response(updated_user_data), 200
            
        elif record == "user":
            updated_user_data = {}
            user_id = request.args.get("id")
            if 'firstname' in request.json:
                updated_user_data['firstname'] = request.json['firstname']
            if 'lastname' in request.json:
                updated_user_data['lastname'] = request.json['lastname']
            if 'birthdate' in request.json:
                updated_user_data['birthdate'] = request.json['birthdate']
            if 'position' in request.json:
                updated_user_data['position'] = request.json['position']
            if 'contact' in request.json:
                updated_user_data['contact'] = request.json['contact']
            if 'course' in request.json:
                updated_user_data['course'] = request.json['course']
            if 'section' in request.json:
                updated_user_data['section'] = request.json['section']
            if not updated_user_data:
                return Messages.json_fail_response("No data passed"), 400

            set_clause = ', '.join([f"{key} = ?" for key in updated_user_data.keys()])
            query = f"UPDATE medics_users SET {set_clause} WHERE user_id = ?"
            params = list(updated_user_data.values()) + [user_id]
            cursor.execute(query, params)
            conn.commit()
            if cursor.rowcount == 0:
                return Messages.json_fail_response("User ID not found"), 404
            else:
                return Messages.json_success_response(updated_user_data), 200
            
        else: 
            return Messages.json_fail_response("Invalid record type"), 400
    
    except Exception as e:
        return Messages.json_fail_response(str(e)), 500
    
    finally: 
        conn.close()


        
@api_bp.route('/delete', methods=['DELETE'])
def httpDel():
    try:
        conn = getDb()
        cursor = conn.cursor()
        record = request.args.get("record") # user or forms

        if record == "user":
            user_id = request.args.get("id")
            user_type = request.args.get("type")

            if not user_id or not user_type:
                return Messages.json_fail_response("Missing id or user type."), 400

            user_id = int(user_id)

            if user_type == "student":
                cursor.execute("DELETE FROM medics_students WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM medics_users WHERE user_id = ?", (user_id,))
            elif user_type in ["employee", "admin"]:
                cursor.execute("DELETE FROM medics_employees WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM medics_users WHERE user_id = ?", (user_id,))
            else: 
                return Messages.json_fail_response("Invalid user type"), 400

            conn.commit()
            return Messages.json_success_response(f"User ID: {user_id} deleted"), 200
        
        elif record == "forms":
            form_id = request.args.get("id")
            form_type = request.args.get("type")

            if not form_id or not form_type:
                return Messages.json_fail_response("Missing id or user type."), 400
            
            form_id = int(form_id)

            if form_type in ["appointment", "emergency", "notification"]:
                cursor.execute("DELETE FROM medics_forms where form_id = ? AND form_type = ?", (form_id, form_type,))
                conn.commit()
                return Messages.json_success_response(f"Form ID: {form_id} deleted"), 200
            else:
                return Messages.json_fail_response("Invalid form type"), 400

        else:
            return Messages.json_fail_response("Invalid record type"), 400

    except Exception as e:
        return Messages.json_fail_response(str(e)), 500

    finally:
        conn.close()