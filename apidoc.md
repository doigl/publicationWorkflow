# PublicationWorkflow
A Flask-API to handle publications of research data

## Version: 1.0.0

**Contact information:**  
fokus@izus.uni-stuttgart.de  

**License:** [MIT](https://mit-license.org/)

### /roles

#### POST
##### Summary:

adds new user

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 422 | unprocessable, user could not be added |  |

### /roles/{identifier}/token

#### GET
##### Summary:

get (new) JSON Web Token for authentication

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| identifier | path | identifier of registered user | Yes | string |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 422 | unprocessable, user could not be added |  |

### /publications

#### GET
##### Summary:

gets all available publications

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |

#### POST
##### Summary:

add a new publication

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| publication | body | The publication to create | No | [Publication](#publication) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 422 | unprocessable, user could not be added |  |

### /publications/{pid}

#### GET
##### Summary:

get the publication with id {pid}

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 422 | unprocessable, user could not be added |  |

#### DELETE
##### Summary:

deletes the publication with id {pid}

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication not found |  |
| 422 | unprocessable, publication could not be deleted |  |

### /publications/{pid}/giveok

#### PATCH
##### Summary:

indicates, that author has finished checklist

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | required information missing |  |
| 409 | WorkflowError, giving ok to already published or exported publication |  |
| 422 | unprocessable, user could not be added |  |

### /publications/{pid}/publish

#### PATCH
##### Summary:

publishes a data publication

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | required information missing |  |
| 409 | WorkflowError, giving ok to already published or exported publication |  |
| 422 | unprocessable, user could not be added |  |

### /publications/{pid}/export

#### PATCH
##### Summary:

exports a data publication

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | required information missing |  |
| 409 | WorkflowError, trying to export publication that is not published |  |
| 422 | unprocessable, user could not be added |  |

### /publications/{pid}/feedbacks

#### GET
##### Summary:

returns all feedback for publication with id {pid}

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication not found |  |

#### POST
##### Summary:

adds a new feedback to publication with id {pid}

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |
| feedback | body |  | No | [FeedbackShort](#feedbackshort) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | text is missing in JSON-Body |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication not found |  |
| 422 | unprocessable, feedback could not be saved in database |  |

### /publications/{pid}/feedbacks/{fid}

#### GET
##### Summary:

gets a specific feedback

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path | ID of the publication | Yes | integer |
| fid | path | ID of the feedback | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication or feedback not found |  |
| 409 | conflict, feedback does not belong to publication |  |

#### PATCH
##### Summary:

changes the text of a specific feedback

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |
| fid | path | ID of the feedback | Yes | integer |
| feedback | body |  | No | [FeedbackShort](#feedbackshort) |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication or feedback not found |  |
| 409 | conflict, feedback does not belong to publication |  |
| 422 | unprocessable, feedback could not be updated |  |

### /publications/{pid}/feedbacks/{fid}/done

#### PATCH
##### Summary:

marks a feedback as done

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| pid | path |  | Yes | integer |
| fid | path |  | Yes | integer |

##### Responses

| Code | Description | Schema |
| ---- | ----------- | ------ |
| 200 | success | object |
| 400 | required information missing |  |
| 401 | authentication missing |  |
| 403 | not allowed, required permission missing |  |
| 404 | publication or feedback not found |  |
| 409 | conflict, feedback does not belong to publication |  |
| 422 | unprocessable, feedback could not be updated |  |

### Models


#### Publication

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | Yes |
| invocationId | string |  | Yes |
| doi | string |  | Yes |
| displayName | string |  | Yes |
| status | string |  | No |
| okAuthor | dateTime |  | No |
| published | dateTime |  | No |
| exported | dateTime |  | No |

#### Feedback

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | Yes |
| text | string |  | Yes |
| done | boolean |  | Yes |
| publication | [Publication](#publication) |  | No |
| author | [Role](#role) |  | No |

#### FeedbackShort

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| text | string |  | Yes |

#### Role

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| id | integer |  | Yes |
| name | string |  | Yes |
| identifier | string |  | No |
| roles | [ string ] |  | No |