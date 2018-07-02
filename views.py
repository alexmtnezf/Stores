# -*- coding: utf-8 -*-
from flask import jsonify, request, url_for
from werkzeug.utils import redirect

from app import flaskApp


@flaskApp.route('/')
def index():
    return redirect('/apidocs')


@flaskApp.route('/home')
def home():
    return jsonify({"message": "Hello, World!"})


# In a protected view, get the claims you added to the jwt with the
# get_jwt_claims() method
@flaskApp.route("/api/protected", methods=["GET"])
@jwt_required
def protected():
    """
    Protected content method.
    ---
    tags:
      - Auth
    description: Protected content method. Can not be seen without valid token.
    responses:
      200:
        description: User successfully accessed the content.
    """
    # Access the identity of the current user identity (username) with get_jwt_identity
    current_identity = get_jwt_identity()
    # user = UserModel.find_by_username(current_identity)
    claims = get_jwt_claims()
    resp = jsonify({
        "protected": "{} - you saw me!".format(current_identity),
        "claims": claims
    })
    resp.status_code = 200

    return resp


ENV_COOKIES = ('_gauges_unique', '_gauges_unique_year', '_gauges_unique_month',
               '_gauges_unique_day', '_gauges_unique_hour', '__utmz', '__utma',
               '__utmb')


@flaskApp.route('/api/cookies')
def view_cookies(hide_env=True):
    """Returns cookie data.
    ---
    tags:
      - Cookies
    produces:
      - application/json
    responses:
      200:
        description: Set cookies..
    """

    cookies = dict(request.cookies.items())

    if hide_env and ('show_env' not in request.args):
        for key in ENV_COOKIES:
            try:
                del cookies[key]
            except KeyError:
                pass

    return jsonify(cookies=cookies)


@flaskApp.route('/api/cookies/set/<name>/<value>')
def set_cookie(name, value):
    """Sets a cookie and redirects to cookie list.
    ---
    tags:
      - Cookies
    parameters:
      - in: path
        name: name
        type: string
      - in: path
        name: value
        type: string
    produces:
      - text/plain
    responses:
      200:
        description: Set cookies and redirects to cookie list.
    """

    r = flaskApp.make_response(redirect(url_for('view_cookies')))
    r.set_cookie(key=name, value=value, secure=secure_cookie())

    return r


@flaskApp.route('/api/cookies/set')
def set_cookies():
    """Sets cookie(s) as provided by the query string and redirects to cookie list.
    ---
    tags:
      - Cookies
    parameters:
      - in: query
        name: freeform
        explode: true
        allowEmptyValue: true
        schema:
          type: object
          additionalProperties:
            type: string
        style: form
    produces:
      - text/plain
    responses:
      200:
        description: Redirect to cookie list
    """

    cookies = dict(request.args.items())
    r = flaskApp.make_response(redirect(url_for('view_cookies')))
    for key, value in cookies.items():
        r.set_cookie(key=key, value=value, secure=secure_cookie())

    return r


@flaskApp.route('/api/cookies/delete')
def delete_cookies():
    """Deletes cookie(s) as provided by the query string and redirects to cookie list.
    ---
    tags:
      - Cookies
    parameters:
      - in: query
        name: freeform
        explode: true
        allowEmptyValue: true
        schema:
          type: object
          additionalProperties:
            type: string
        style: form
    produces:
      - text/plain
    responses:
      200:
        description: Redirect to cookie list
    """

    cookies = dict(request.args.items())
    r = flaskApp.make_response(redirect(url_for('view_cookies')))
    for key, value in cookies.items():
        r.delete_cookie(key=key)

    return r


@flaskApp.route('/api/colors/<palette>/')
def colors(palette):
    """Example endpoint returning a list of colors by palette
    This is using docstrings for specifications.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)
