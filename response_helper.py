from flask import jsonify, send_file
from flask import Response
import logging
import os


def create_error_response(message, app):
    app.logger.info("Validation error {}".format(message))
    resp = jsonify({'message': message, "status": 400})
    resp.status_code = 400
    return resp


def create_parameter_missing_error_response(message, app):
    app.logger.info("Parameter missing error {}".format(message))
    resp = jsonify({'message': message, "status": 422})
    resp.status_code = 422
    return resp


def create_authorization_error_response(message, app):
    app.logger.info("UnAuthorize {}".format(message))
    resp = jsonify({'message': message, "status": 401})
    resp.status_code = 401
    return resp


def create_success_response(message,  app):
    app.logger.info("Response served successfully".format(message))
    resp = jsonify({'message': message, "status": 200})
    resp.status_code = 200
    return resp


def create_success_file_response(absolute_file_name, file_path):
    return send_file(absolute_file_name,
                     mimetype='application/json',
                     attachment_filename=file_path,
                     as_attachment=True)


def create_server_error_response(app):
    app.logger.error("Server Error")
    resp = jsonify({'message': "something went wrong please try again later.", "status": 500})
    resp.status_code = 500
    return resp


def create_health_check_response():
    resp = jsonify({'message': "Application is working...", "status": 200})
    resp.status_code = 200
    return resp
