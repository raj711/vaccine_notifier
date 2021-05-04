from flask import Flask, request, render_template
import json
import logging
import requests
import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__))
dot_env_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dot_env_path)


import email_service, db_service
import response_helper
import atexit
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


# print("ENVIORNMENT..........", os.environ.get("COWIN_API_ENDPOINT"))

app = Flask(__name__)
app_logger = logging.getLogger(os.environ.get("APP_LOGGER"))
app.logger.handlers = app_logger.handlers
app.logger.setLevel(logging.DEBUG)


def get_json_data(district_code, date):
    params = {
        "district_id": district_code,
        "date": date
    }

    url = os.environ.get("COWIN_API_ENDPOINT")

    response = requests.get(url, params=params)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        res = json.loads(response.text)
        return res
    else:
        return None


def find_available_vaccine_slots():
    try:
        app.logger.info("finding available slots.....")
        user_data = db_service.get_user_data()
        vaccine_slots_by_district = {}
        for data in user_data:
            # print(data)
            if vaccine_slots_by_district.get(str(data.get("district")) + '_' + str(data.get("age")), None) is None:
                res = get_json_data(data.get("district"), datetime.strftime(datetime.now(), "%d-%m-%Y"))
                if res is None:
                    app.logger.info("Currently not available.....")

                available_centers = res.get("centers")
                booking_available = []
                for center in available_centers:
                    center_name = center.get("name")
                    center_fee = center.get("fee_type")
                    center_pincode = center.get("pincode")
                    sessions = center.get("sessions")
                    available_session = []
                    for session in sessions:
                        if session.get("available_capacity") > 0 and int(session.get("min_age_limit")) == int(data.get("age")):
                            available_session.append(session)

                    if len(available_session) > 0:
                        center_data = {
                            "name": center_name,
                            "fee": center_fee,
                            "pincode": center_pincode,
                            "sessions": available_session
                        }
                        booking_available.append(center_data)
                vaccine_slots_by_district[str(data.get("district")) + '_' + str(data.get("age"))] = booking_available
                # print(vaccine_slots_by_district)

            if vaccine_slots_by_district[str(data.get("district")) + '_' + str(data.get("age"))] == []:
                continue
            email_sent = email_service.send_email(data.get("email"), vaccine_slots_by_district[str(data.get("district")) + '_' + str(data.get("age"))])
            if email_sent:
                db_service.update_user_notified_status(data.get("email"), data.get("district"),
                                                       data.get("age"), False)
                app.logger.info("Email sent successfully....")
            else:
                app.logger.info("Error in sending email...")
            # Email function
    except Exception as e:
        app.logger.error("Something Wrong... {}".format(str(e)))
        print(str(e))


find_available_vaccine_slots()

def job():
    print("Scheduler started.....")
    find_available_vaccine_slots()

sched = BackgroundScheduler(daemon=True)
sched.add_job(job, trigger='interval', minutes=int(os.environ.get("TRIGGER_TIME_MINUTES")))
sched.start()

atexit.register(lambda: sched.shutdown())

@app.route('/subscribe', methods=['GET'])
def subscribe():
    try:
        email = request.args.get("email")
        district_code = request.args.get("district")
        age = request.args.get("age")
        if district_code is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("district_code"), app)
        elif age is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("age"), app)
        elif email is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("email"), app)
        else:

            updated = db_service.update_user_notified_status(email, district_code, age, True)
            if updated:
                return response_helper.create_success_response("Subscription added successfully..", app)
            else:
                return response_helper.create_error_response("Please Try again..", app)
    except Exception as e:
        app.logger.info("Something went wrong... {}".format(str(e)))
        return response_helper.create_server_error_response(app)


@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        print(request.json)
        req_body = request.json
        district_code = req_body.get("district_code", None)
        age = req_body.get("age", None)
        email = req_body.get("email", None)

        if district_code is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("district_code"), app)
        elif age is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("age"), app)
        elif email is None:
            return response_helper.create_parameter_missing_error_response('{} is required parameter'.format("email"), app)
        else:
            user = db_service.get_user_by_email(email, district_code, age)
            if user is None or user == []:
                user_inserted = db_service.create_user(email, district_code, age)
                if user_inserted:
                    return response_helper.create_success_response("Subscription added..", app)
                else:
                    return response_helper.create_error_response("Error... Please Try again", app)
            elif user[0].get("is_notified") == 1:
                user_updated = db_service.update_user_notified_status(email, district_code, age, True)
                if user_updated:
                    return response_helper.create_success_response("Subscription Added..", app)
                else:
                    return response_helper.create_error_response("Error... Please Try again", app)
            else:
                return response_helper.create_success_response("Already Subscribed", app)

    except Exception as e:
        app.logger.error("Something wrong.. {}".format(str(e)))
        return response_helper.create_server_error_response(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
