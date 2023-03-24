from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify

routes = Blueprint("routes", __name__)

@routes.route('/')
@routes.route("/index", methods=["GET"])
def index():
    return render_template("index.html")