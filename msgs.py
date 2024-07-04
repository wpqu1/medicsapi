from flask import jsonify, request

 # Pre-formatted JSON response messages for errors and successes.

class Messages:
    
    # Fail Responses

    @staticmethod
    def json_error_invalid_parameters(props="variable not set"):
        return jsonify({
            'status': 'fail',
            'message': f'Invalid Payload Properties: {props}'
        })

    @staticmethod
    def json_error_required_fields_not_filled():
        return jsonify({
            'status': 'fail',
            'message': 'Required fields were not filled.'
        })

    @staticmethod
    def json_error_module_not_exist(uri):
        return jsonify({
            'status': 'fail',
            'message': 'Requested module not found.',
            'data': {
                'uri': uri
            }
        })

    @staticmethod
    def json_error_data_already_exists(duplicate_value):
        return jsonify({
            'status': 'fail',
            'message': 'Data already exists in the database.',
            'data': {
                'duplicate_value': duplicate_value
            }
        })

    @staticmethod
    def json_database_error(message='Please try again.'):
        return jsonify({
            'status': 'fail',
            'message': f'Database Error: {message}'
        })

    @staticmethod
    def json_fail_response(data):
        return jsonify({
            'status': 'fail',
            'message': data,
            'method': request.method
        })

    # Success Responses

    @staticmethod
    def json_success_response(data):
        return jsonify({
            'status': 'success',
            'data': data,
            'method': request.method
        })
