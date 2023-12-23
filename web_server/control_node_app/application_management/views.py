from application_management import application_management_blue
from flask import request

@application_management_blue.route('/add', methods=['POST'])
def add_application():
    json_file = request.get_json()
    print(json_file)
    return 'addApplication'

@application_management_blue.route('/getall')
def get_all_applications():
    return 'getAllApplications'

@application_management_blue.route('/get/<string:application_id>')
def get_application(application_id):
    print(application_id)
    return 'getApplication'

@application_management_blue.route('/delete/<string:application_id>')
def delete_application(application_id):
    print(application_id)
    return 'deleteApplication'

@application_management_blue.route('/update/<string:application_id>', methods=['POST'])
def update_application(application_id):
    json_file = request.get_json()
    print(json_file)
    return 'updateApplication'

@application_management_blue.route('/start/<string:application_id>')
def start_application(application_id):
    print(application_id)
    return 'startApplication'

@application_management_blue.route('/stop/<string:application_id>')
def stop_application(application_id):
    print(application_id)
    return 'stopApplication'

@application_management_blue.route('/restart/<string:application_id>')
def restart_application(application_id):
    print(application_id)
    return 'restartApplication'


