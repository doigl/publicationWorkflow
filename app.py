from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from models.db import db, setup_db
from models.publication import Publication
from models.feedback import Feedback
from models.role import Role
from models.errors import PublicationValidationError, WorkflowError, AuthError
from auth import requires_auth, encode_jwt, randomString, get_hash
from collections.abc import Iterable

app = Flask(__name__)
setup_db(app)
migrate = Migrate(app, db)

def check_request(request):
    ### checks, if request entails json-body ###
    if request.json is None:
        abort(400, 'No JSON-Body')


@app.route('/roles/<string:pid>/token', methods=["GET"])
def get_token(pid):
    person = Role.query.filter_by(identifier=get_hash(pid)).first()
    if person is None:
        abort(404)
    payload = {}
    payload["roles"] = person.get_roles()
    payload["name"] = person.name
    payload["email"] = person.email
    payload["id"] = person.id
    response = {
        'success': True,
        'token': encode_jwt(payload)
    }
    return jsonify(response)


@app.route('/roles', methods=['POST'])
@requires_auth('add:user')
def add_user(payload):
    check_request(request)
    new_name = request.json.get('name')
    new_email = request.json.get('email')
    if new_email is None:
        new_email = ''
    new_roles = request.json.get('roles')

    if new_name is None:
        abort(400)
    try:
        person = Role(new_name, new_email)
        identifier = randomString(24)
        person.identifier = get_hash(identifier)
        person.insert()
        if new_roles is not None and isinstance(new_roles, Iterable):
            for role in new_roles:
                person.add_role(role)
    except Exception as e:
        abort(422, e)
    response = {
        'success': True,
        'person': person.format(),
        'identifier': identifier
        }
    return jsonify(response)


@app.route('/publications')
@requires_auth('get:publications')
def get_all_publications(payload):
    publications = Publication.query.all()
    response = {'success': True,
                'publications': [p.format() for p in publications]
                }
    return jsonify(response)


@app.route('/publications/<int:pub_id>', methods=["GET"])
@requires_auth('get:publication')
def get_publication(payload, pub_id):
    publication = Publication.query.get(pub_id)
    if publication is None:
        abort(404)
    response = {'success': True,
                'publication': publication.format()
                }
    return jsonify(response)


@app.route('/publications', methods=["POST"])
@requires_auth('post:publication')
def new_publication(payload):
    check_request(request)
    new_datasetId = request.json.get("datasetId")
    new_invocationId = request.json.get('invocationId')
    new_displayName = request.json.get('datasetDisplayName')
    new_doi = request.json.get('datasetGlobalId')

    missing = []

    if new_datasetId is None:
        missing.append("datasetId")
    if new_invocationId is None:
        missing.append("invocationId")
    if new_displayName is None:
        missing.append("datasetDisplayName")
    if new_doi is None:
        missing.append("datasetGlobalId")

    if len(missing) > 0:
        raise PublicationValidationError(
            'The following field{} missing: {}'.format(
                ' is' if len(missing) == 1 else 's are',
                ", ".join(missing)),
            400)

    pub = Publication(doi=new_doi,
                      invocId=new_invocationId,
                      databaseId=new_datasetId,
                      displayName=new_displayName)
    try:
        pub.insert()
    except Exception as e:
        abort(422, e)

    response = {
        'success': True,
        'created': pub.id,
        'publication': pub.format()
    }

    return jsonify(response)


@app.route('/publications/<int:pub_id>', methods=["DELETE"])
@requires_auth('delete:publication')
def deletePublication(payload, pub_id):
    publication = Publication.query.get(pub_id)
    if publication is None:
        abort(404)
    try:
        publication.delete()
    except Exception as e:
        abort(422, e)

    response = {'success': True,
                'deleted': publication.id}
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks', methods=['GET'])
@requires_auth('get:feedback')
def get_feedbacks_of_publication(payload, pid):
    pub = Publication.query.get(pid)
    if pub is None:
        abort(404)
    response = {
        'success': True,
        'publication': pub.format(),
        'feedbacks': [f.format() for f in pub.feedbacks]
    }
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks', methods=['POST'])
@requires_auth('post:feedback')
def add_feedback_to_publication(payload, pid):
    pub = Publication.query.get(pid)
    if pub is None:
        abort(404)
    check_request(request)
    feedback_text = request.json.get('text')
    if feedback_text is None or feedback_text == '':
        abort(400)
    author_id = payload['id']
    fb = Feedback(pid, feedback_text, author_id)
    pub.feedbacks.append(fb)
    try:
        pub.update()
    except Exception as e:
        abort(422, e)

    response = {
        'success': True,
        'created': fb.id,
        'feedback': fb.format()}
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks/<int:fid>', methods=['GET'])
@requires_auth('get:feedback')
def get_feedback(payload, pid, fid):
    fb = Feedback.query.get(fid)
    if fb is None:
        abort(404)
    if fb.publication.id != pid:
        abort(409)

    response = {
        'success': True,
        'feedback': fb.format()
    }
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks/<int:fid>', methods=['PATCH'])
@requires_auth('patch:feedback')
def change_feedback(payload, pid, fid):
    fb = Feedback.query.get(fid)
    if fb is None:
        abort(404)
    if fb.publication.id != pid:
        abort(409)
    check_request(request)
    new_text = request.json.get('text')
    done = request.json.get('done')

    if new_text is None and done is None:
        abort(400)

    if new_text is not None:
        fb.feedback = new_text

    if done is not None:
        fb.done = done
    try:
        fb.update()
    except Exception as e:
        abort(422, e)

    response = {
        'success': True,
        'changed': fb.id,
        'feedback': fb.format()
    }
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks/<int:fid>/done',
           methods=['PATCH'])
@requires_auth('complete:feedback')
def mark_feedback_as_done(payload, pid, fid):
    fb = Feedback.query.get(fid)
    if fb is None:
        abort(404)
    if fb.publication.id != pid:
        abort(409)
    check_request(request)
    done = request.json.get('done')

    if done is None:
        abort(400)
    else:
        fb.done = done

    try:
        fb.update()
    except Exception as e:
        abort(422, e)

    response = {
        'success': True,
        'changed': fb.id,
        'feedback': fb.format()
    }
    return jsonify(response)


@app.route('/publications/<int:pid>/feedbacks/<int:fid>', methods=['DELETE'])
@requires_auth('delete:feedback')
def delete_feedback(payload, pid, fid):
    fb = Feedback.query.get(fid)
    if fb is None:
        abort(404)
    if fb.publication.id != pid:
        abort(409)
    try:
        fb.delete()
    except Exception as e:
        abort(422, e)

    response = {
        'success': True,
        'deleted': fb.id
    }
    return jsonify(response)


@app.route('/publications/<int:pid>/publish', methods=['PATCH'])
@requires_auth('publish:publication')
def publish_publication(payload, pid):
    pub = Publication.query.get(pid)
    if pub is None:
        abort(404)
    pub.actualize_status()
    if pub.status == 'exported':
        raise WorkflowError('Publication is already exported', 409)
    elif pub.status == 'published':
        raise WorkflowError('Publication is already published', 409)
    elif pub.status == 'feedbacks to to':
        raise WorkflowError('There are feedbacks to do before publication',
                            409)
    elif pub.status == 'finished':
        try:
            pub.publish()
        except Exception as e:
            abort(422, e)
        response = {
            'success': True,
            'publication': pub.format()
        }
    else:
        raise WorkflowError(
            'Publication is in unknown status: {}'.format(pub.status),
            409
        )
    return jsonify(response)


@app.route('/publications/<int:pid>/export', methods=['PATCH'])
@requires_auth('export:publication')
def export_publication(payload, pid):
    pub = Publication.query.get(pid)
    if pub is None:
        abort(404)

    pub.actualize_status()

    if pub.status != 'published':
        raise WorkflowError('Only published publication can be exported', 409)
    else:
        try:
            pub.export()
        except Exception as e:
            abort(422, e)
        response = {
            'success': True,
            'publication': pub.format()
        }
    return jsonify(response)


@app.route('/publications/<int:pid>/giveok', methods=['PATCH'])
@requires_auth('giveokto:publication')
def giveok2publication(payload, pid):
    pub = Publication.query.get(pid)
    if pub is None:
        abort(404)
    pub.actualize_status()
    if pub.status == 'exported':
        raise WorkflowError('Publication is already exported', 409)
    elif pub.status == 'published':
        raise WorkflowError('Publication is already published', 409)
    try:
        pub.registerOk()
    except Exception as e:
        abort(422, e)
    response = {
        'success': True,
        'publication': pub.format()
    }
    return jsonify(response)


###
# Error Handling
###


@app.errorhandler(404)
def not_found_404(error):
    """
    Errorhandler for 404 (ressource not found) error
    """

    response = jsonify({'success': False,
                        'error': 404,
                        'message': 'resource not found'}), 404
    return response


@app.errorhandler(405)
def not_allowed_405(error):
    """
    Errorhandler for 405 (method not allowed) error
    """
    response = jsonify({'success': False,
                        'error': 405,
                        'message': 'method not allowed'}), 405
    return response


@app.errorhandler(409)
def conflict_409(error):
    """
    Errorhandler for 405 (method not allowed) error
    """
    response = jsonify({'success': False,
                        'error': 409,
                        'message':
                            'conflict: feedback does not belong to publication'
                        }, 409)
    return response


@app.errorhandler(422)
def not_proccessable_422(error):
    """
    Errorhandler for 422 (request not proccessable) error
    """
    response = jsonify({
      'success': False,
      'error': 422,
      'message': 'request not processable: {}'.format(error)}), 422
    return response


@app.errorhandler(400)
def bad_request_400(error):
    """
    Errorhandler for 400 (bad request) error,
    used in this API for missing information in the request
    """
    response = jsonify({'success': False,
                        'error': 400,
                        'message': 'information missing'}), 400
    return response


@app.errorhandler(500)
def internal_server_error_500(error):
    response = jsonify({'success': False,
                        'error': 500,
                        'message': 'internal server error'}), 500
    return response


@app.errorhandler(PublicationValidationError)
def publication_error(error):
    ###
    # Error handler for publication validation errors
    # Returns 400 response codes
    ###
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code


@app.errorhandler(WorkflowError)
def workflow_error(error):
    ###
    # Error handler for publication validation errors
    # Returns 400 response codes
    ###
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code


@app.errorhandler(AuthError)
def auth_error(error):
    ###
    # Error handler for authentication errors
    # Returns 400, 401 or 403 response codes
    ###

    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error["description"]
                    }), error.status_code
