# publicationWorkflow
A Flask-API to handle publications of research data

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) is an extension that handles SQLAlchemy database migrations for Flask applications using Alembic.

- [PyJWT](https://pyjwt.readthedocs.io/en/latest/) is a Python library which allows you to encode and decode JSON Web Tokens (JWT).

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run
```

### Runing the tests 

From the /tests-Directory, run 
```bash
python -m unittest
```

## API Documentation

The trivia-API functions as a backend for the trivia-frontend. It offers endpoints to get available questions (also per category), add new questions and deliver random questions for the game. 

### Datatypes and Errors

The API consumes and returns JSON-Objects. Status code for successful API-Requests is always _200_. Every answer object includes a _success_ attribute with the value _True_ if the request can be responed successful and the value _False_ in case of an error.

Error Objects have the following structure:
```
{
    'success': False,
    'error': <status-code, for example 404>,
    'message': '<errormsg, for example _file not found_>'
}

```

Expectable Errors:
| Status Code | Error message | Explanation|
| --- | --- | --- |
| 400 | bad request | a required parameter was not supplied |
| 401 | unauthorized | you did not authenticate successfully against the service |
| 403 | forbidden | authentication was successfull, but you do not have the required permission |
| 404 | resource not found | the resource you requested is not available, for example a non existing endpoint, a non existing publication or a non existing feedback |
| 405 | method not allowed | the method (GET, POST, PUT, PATCH, DELETE) you used is not supported by the endpoint |
| 409 | conflict | request asks for something inconsistent, for example a feedback with a inconsistent publication or a workflow step that is noch allowed in this status |
| 422 | not processable | the request could not be processed |
| 500 | internal server error | an error on server side prevented the response to the request|

### Authentification
The API uses Java Web Tokens (JWT) for Authentication. As a registered user, you can get or renew your Token with the GET /token/<string:identifier> Endpoint, using your identifier.

Add this token as a bearer token to the "Authorization"-Header. 

´´´Authorization: bearer <token>```


