import unittest
import os
import sys
sys.path.append('..')
from app import app
from auth import randomString, encode_jwt, decode_jwt


class Test_Pubworkflow(unittest.TestCase):

    # adapted from https://pynative.com/python-generate-random-string/
    def setUp(self):
        self.app = app
        admin = {}
        admin["roles"] = ['Admin']
        admin["name"] = 'Admin'
        admin["email"] = 'admin@publicationWorkflow.de'
        admin["id"] = '1'
        self.admin_token = encode_jwt(admin)

        noob = {}
        noob["name"] = 'Noob'
        noob["email"] = 'noob@publicationWorkflow.de'
        self.noob_token = encode_jwt(noob)

        hacker = {}
        hacker['roles'] = ['Hacker']
        hacker["name"] = 'Hacker'
        hacker["email"] = 'hacker@publicationWorkflow.de'
        self.hacker_token = encode_jwt(hacker)

        author = {}
        author["roles"] = ['Author']
        author["name"] = 'Autor'
        author["email"] = 'autor@publicationWorkflow.de'
        author["id"] = '2'
        self.author_token = encode_jwt(author)

        curator = {}
        curator["roles"] = ['Curator']
        curator["name"] = 'Curator'
        curator["email"] = 'curator@publicationWorkflow.de'
        curator["id"] = '3'
        self.curator_token = encode_jwt(curator)

        self.client = self.app.test_client
        self.databaseFilename = 'test_pubworkflow.db'
        project_dir = os.path.dirname(os.path.abspath(__file__))
        self.databasePath = 'sqlite:///{}'.format(os.path.join(project_dir,
                                                  self.databaseFilename))
        self.newPublication = {'datasetId': 254,
                               'invocationId': randomString(12),
                               'datasetDisplayName':
                                   'new Dataset with interesting title',
                               'datasetGlobalId': 'doi:10.76764/darus-442'}

    def make_header(self, role):
        if role == 'Admin':
            token = self.admin_token
        elif role == 'Curator':
            token = self.curator_token
        elif role == 'Author':
            token = self.author_token
        else:
            token = self.noob_token
        return {"Authorization": "bearer {}".format(token)}

    def check_success(self, response):
        data = response.json
        if response.status_code != 200:
            print(data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data.get('success'))

    def check_error(self, response, code=None, message=None):
        data = response.json
        self.assertFalse(data.get('success'))
        if message is not None:
            self.assertEqual(data.get('message'), message)
        if code is not None:
            self.assertEqual(response.status_code, code)
            self.assertEqual(data.get('error'), code)

    def get_existing_pid(self):
        response = self.client().get(
            '/publications',
            headers=self.make_header('Admin'))
        pubs = response.json.get('publications')
        if len(pubs) == 0:
            # if there are no publications in database, add a new one #
            newPub = {'datasetId': 255,
                      'invocationId': randomString(12),
                      'datasetDisplayName':
                      'new Dataset with even more interesting title',
                      'datasetGlobalId': 'doi:10.76764/darus-447'}
            response = self.client().post('/publications', json=newPub)
            p_id = response.json.get('created')
        else:
            # else take the first publication #
            p_id = pubs[0]["id"]
        return p_id

    def test_create_user(self):
        new_user = {
            'name': 'testuser',
            'email': 'testuser@test.de',
            'roles': ['Author']
        }
        response = self.client().post(
            '/roles',
            json=new_user,
            headers=self.make_header('Admin'))
        self.check_success(response)
        self.assertIn('identifier', response.json)
        identifier = response.json.get('identifier')

        # get token and compare information #
        response = self.client().get('/roles/{}/token'.format(identifier))
        self.check_success(response)
        self.assertIn('token', response.json)
        token = response.json.get('token')
        payload = decode_jwt(token)
        self.assertEqual(payload["roles"], new_user['roles'])
        self.assertEqual(payload["name"], new_user["name"])
        self.assertEqual(payload["email"], new_user["email"])

    def test_getPublications(self):
        response = self.client().get(
            '/publications',
            headers=self.make_header('Admin')
        )
        self.check_success(response)

    def test_get_non_existing_path(self):
        response = self.client().get(
            '/publicatoins',
            headers=self.make_header('Admin'))
        self.check_error(response, 404)

    def test_create_get_deletePublication(self):
        # create new publication #
        response = self.client().post('/publications',
                                      json=self.newPublication,
                                      headers=self.make_header('Admin'))
        self.check_success(response)
        pubId = response.json.get('created')

        # get newly created publication #
        response = self.client().get(
            '/publications/{}'.format(pubId),
            headers=self.make_header('Author'))
        self.check_success(response)
        publication = response.json.get('publication')
        self.assertEqual(publication['status'], 'finished')
        self.assertEqual(publication['doi'],
                         self.newPublication['datasetGlobalId'])
        self.assertEqual(publication['displayName'],
                         self.newPublication['datasetDisplayName'])
        self.assertEqual(publication['invocationId'],
                         self.newPublication['invocationId'])

        # try to post the same publication again, expecting 422 #
        response = self.client().post('/publications',
                                      json=self.newPublication,
                                      headers=self.make_header('Admin'))
        self.check_error(response, 422)

        # delete newly created publication #
        response = self.client().delete(
            '/publications/{}'.format(pubId),
            headers=self.make_header('Admin'))
        self.check_success(response)
        self.assertEqual(response.json.get('deleted'), pubId)

    def test_get_unexistingPublication(self):
        response = self.client().get(
            '/publications/999',
            headers=self.make_header('Author'))
        self.check_error(response, 404)

    def test_delete_unexistingPublication(self):
        response = self.client().delete(
            '/publications/999',
            headers=self.make_header('Admin'))
        self.check_error(response, 404)

    def test_create_publication_with_missing_data(self):
        keys = self.newPublication.keys()
        for key in keys:
            uncompletePub = self.newPublication
            oldval = uncompletePub[key]
            uncompletePub[key] = None
            response = self.client().post(
                '/publications',
                headers=self.make_header('Admin'),
                json=uncompletePub)
            self.check_error(response,
                             400,
                             'The following field is missing: {}'.format(key))
            self.newPublication[key] = oldval

    def test_create_change_delete_feedback(self):
        # Find publication to add feedback #
        p_id = self.get_existing_pid()
        # create new Feedback #
        newFeedback = {
            'text':
                "Please try to add some more metadata "
                "to the engineering metadata."}
        # add feedback to publication #
        response = self.client().post(
            '/publications/{}/feedbacks'.format(p_id),
            headers=self.make_header('Curator'),
            json=newFeedback)
        self.check_success(response)
        self.assertIn('created', response.json)
        fid = response.json['created']

        # get all feedbacks of publication #
        response = self.client().get(
            '/publications/{}/feedbacks'.format(p_id),
            headers=self.make_header('Author'))
        self.check_success(response)
        in_feedbacks = False
        for fb in response.json.get('feedbacks'):
            in_feedbacks = in_feedbacks or fb['id'] == fid
        self.assertTrue(in_feedbacks)

        # get specific feedback #
        response = self.client().get(
            '/publications/{}/feedbacks/{}'.format(p_id, fid),
            headers=self.make_header('Author'))
        self.check_success(response)
        feedback = response.json.get('feedback')
        self.assertEqual(feedback['id'], fid)
        self.assertEqual(feedback['text'], newFeedback['text'])
        self.assertIn('author', feedback)
        self.assertEqual(feedback['publication']['id'], p_id)
        self.assertFalse(feedback['done'])

        # change feedback text #
        newText = 'new Feedbacktext'
        response = self.client().patch(
            '/publications/{}/feedbacks/{}'.format(p_id, fid),
            headers=self.make_header('Curator'),
            json={'text': newText}
        )
        self.check_success(response)
        feedback = response.json.get('feedback')
        self.assertEqual(feedback["text"], newText)

        # mark feedback as done #
        response = self.client().patch(
            '/publications/{}/feedbacks/{}/done'.format(p_id, fid),
            headers=self.make_header('Author'),
            json={'done': True}
        )
        self.check_success(response)
        feedback = response.json.get('feedback')
        self.assertTrue(feedback["done"])

        # try to change feedback without information, expecting 400 #
        response = self.client().patch(
            '/publications/{}/feedbacks/{}'.format(p_id, fid),
            headers=self.make_header('Curator'),
            json={'something false': 1}
        )
        self.check_error(response, 400)

        # delete feedback #
        response = self.client().delete(
            '/publications/{}/feedbacks/{}'.format(p_id, fid),
            headers=self.make_header('Curator')
        )
        self.check_success(response)
        self.assertEqual(response.json.get('deleted'), fid)

    def test_get_feedbacks_of_non_existing_publication(self):
        response = self.client().get(
            '/publications/999/feedbacks',
            headers=self.make_header('Author'))
        self.check_error(response, 404)

    def test_get_change_delete_non_existing_feedback(self):
        pid = self.get_existing_pid
        response = self.client().patch(
            '/publications/{}/feedbacks/999'.format(pid),
            headers=self.make_header('Curator'))
        self.check_error(response, 404)

        response = self.client().get(
            '/publications/{}/feedbacks/999'.format(pid),
            headers=self.make_header('Curator'))
        self.check_error(response, 404)

        response = self.client().delete(
            '/publications/{}/feedbacks/999'.format(pid),
            headers=self.make_header('Curator'))
        self.check_error(response, 404)

    def test_workflow(self):
        # create new publication: status = created
        new_publication = {'datasetId': 256,
                           'invocationId': randomString(12),
                           'datasetDisplayName':
                               'some new Dataset for testing',
                           'datasetGlobalId': 'doi:10.76764/darus-450'}
        response = self.client().post(
            '/publications',
            json=new_publication,
            headers=self.make_header('Admin'))
        publication = response.json.get('publication')
        pid = response.json.get('created')
        self.assertEqual(publication.get('status'), 'finished')
        # add feedback: status = feedbacks to do
        new_feedback = {'text': 'Something to do'}
        response = self.client().post(
            '/publications/{}/feedbacks'.format(pid),
            json=new_feedback,
            headers=self.make_header('Curator'))
        fid = response.json.get('created')
        publication = response.json.get('feedback').get('publication')
        self.assertEqual(publication.get('status'), 'feedbacks to do')

        # trying to publish publication with feedbacks to do,
        # expecting 409
        response = self.client().patch(
            '/publications/{}/publish'.format(pid),
            headers=self.make_header('Admin'))
        self.check_error(response, 409)

        # mark feedback as done: status = ok
        response = self.client().patch(
            '/publications/{}/feedbacks/{}/done'.format(pid, fid),
            json={'done': True},
            headers=self.make_header('Author')
        )
        publication = response.json.get('feedback').get('publication')
        self.assertEqual(publication.get('status'), 'finished')

        # give ok from user
        response = self.client().patch(
            '/publications/{}/giveok'.format(pid),
            headers=self.make_header('Author')
        )
        self.check_success(response)
        publication = response.json.get("publication")
        self.assertIn('okAuthor', publication)

        # try to export dataset before publication
        # expecting 409
        response = self.client().patch(
            '/publications/{}/export'.format(pid),
            headers=self.make_header('Admin')
        )
        self.check_error(response, 409)

        # publish dataset: status = published
        response = self.client().patch(
            '/publications/{}/publish'.format(pid),
            headers=self.make_header('Admin')
        )
        self.check_success(response)
        publication = response.json.get('publication')
        self.assertEqual(publication.get('status'), 'published')
        self.assertIn('published', publication)

        # try to give ok after publication
        # expecting 409
        response = self.client().patch(
            '/publications/{}/giveok'.format(pid),
            headers=self.make_header('Author')
        )
        self.check_error(response, 409)

        # export dataset: status = exported
        response = self.client().patch(
            '/publications/{}/export'.format(pid),
            headers=self.make_header('Admin')
        )
        self.check_success(response)
        publication = response.json.get('publication')
        self.assertEqual(publication.get('status'), 'exported')
        self.assertIn('exported', publication)

        # try to give ok after export
        # expecting 409
        response = self.client().patch(
            '/publications/{}/giveok'.format(pid),
            headers=self.make_header('Author')
        )
        self.check_error(response, 409)

    def test_no_header(self):
        response = self.client().get('/publications')
        self.check_error(response, 401, 'authorization header is missing')

    def test_malformed_header(self):
        response = self.client().get(
            'publications',
            headers={'Authorization': 'blablub'})
        self.check_error(
            response,
            401,
            'authentication header malformed. No bearer')

    def test_no_roles(self):
        response = self.client().get(
            'publications',
            headers={'Authorization': 'bearer {}'. format(self.noob_token)})
        self.check_error(
            response,
            400,
            'no roles in token')

    def test_no_permissions(self):
        response = self.client().get(
            'publications',
            headers={'Authorization': 'bearer {}'. format(self.hacker_token)})
        self.check_error(
            response,
            403,
            'required permission {} is not granted'.format('get:publications'))

    def test_rights_get_publications(self):
        # check rights of GET /publications #
        response = self.client().get(
            '/publications',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().get(
            '/publications',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().get(
            '/publications',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_get_publication(self):
        # check rights of GET /publication #
        response = self.client().get(
            '/publications/1',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1',
            headers=self.make_header('Author'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_get_feedbacks(self):
        # check rights of GET /publications/<pid>/feedbacks #
        response = self.client().get(
            '/publications/1/feedbacks',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1/feedbacks',
            headers=self.make_header('Author'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1/feedbacks',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_get_feedback(self):
        # check rights of GET /publications/<pid>/feedbacks/<feedbackid> #
        response = self.client().get(
            '/publications/1/feedbacks/1',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1/feedbacks/1',
            headers=self.make_header('Author'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().get(
            '/publications/1/feedbacks/1',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_delete_publication(self):
        # check rights of delte /publication/<int:pid> #
        response = self.client().delete(
            '/publications/999',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().delete(
            '/publications/999',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().delete(
            '/publications/999',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_delete_feedback(self):
        # check rights of delete /publication/<int:pid>/feedbacks/<int:fid> #
        response = self.client().delete(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().delete(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().delete(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_post_roles(self):
        # check rights of POST /roles #
        response = self.client().post(
            '/roles',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().post(
            '/roles',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().post(
            '/roles',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_post_publications(self):
        # check rights of POST /publications #
        response = self.client().post(
            '/publications',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().post(
            '/publications',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().post(
            '/publications',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_post_feedback(self):
        # check rights of POST /publications/<pid>/feedbacks #
        response = self.client().post(
            '/publications/999/feedbacks',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().post(
            '/publications/999/feedbacks',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().post(
            '/publications/999/feedbacks',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_patch_feedback(self):
        # check rights of PATCH /publications/<pid>/feedbacks/<fid> #
        response = self.client().patch(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/feedbacks/999',
            headers=self.make_header('Curator'))
        self.assertNotEqual(response.status_code, 403)

    def test_rights_patch_feedback_done(self):
        # check rights of PATCH /publications/<pid>/feedbacks/<fid>/done #
        response = self.client().patch(
            '/publications/999/feedbacks/999/done',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/feedbacks/999/done',
            headers=self.make_header('Author'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/feedbacks/999/done',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_publish_publication(self):
        # check rights of PATCH /publications/<pid>/publish #
        response = self.client().patch(
            '/publications/999/publish',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/publish',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/publish',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_export(self):
        # check rights of PATCH /publications/<pid>/export #
        response = self.client().patch(
            '/publications/999/export',
            headers=self.make_header('Admin'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/export',
            headers=self.make_header('Author'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/export',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)

    def test_rights_giveok(self):
        # check rights of PATCH /publications/<pid>/giveok #
        response = self.client().patch(
            '/publications/999/giveok',
            headers=self.make_header('Admin'))
        self.assertEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/giveok',
            headers=self.make_header('Author'))
        self.assertNotEqual(response.status_code, 403)
        response = self.client().patch(
            '/publications/999/giveok',
            headers=self.make_header('Curator'))
        self.assertEqual(response.status_code, 403)
