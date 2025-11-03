# Coffee Shop Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

**Create Virtual Environment**
To create a virtual environment, go to your project’s directory and run the following command. This will create a new virtual environment in a local folder named .venv:

python3 -m venv .venv

**Activate Virtual Environment**
Activating a virtual environment will put the virtual environment-specific python and pip executables into your shell’s PATH.

source .venv/bin/activate

To confirm the virtual environment is activated, check the location of your Python interpreter:

which python

While the virtual environment is active, the above command will output a filepath that includes the .venv directory, by ending with the following:

.venv/bin/python

**Deactivate Virtual Environment**

deactivate

**Reactivate Virtual Environment**
If you want to reactivate an existing virtual environment, follow the same instructions about activating a virtual environment. There’s no need to create a new virtual environment.

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=api.py;
```

To run the server, execute:

```bash
flask run --reload

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes 

flask run --cert=cert.pem --key=key.pem --reload
```




The `--reload` flag will detect file changes and restart the server automatically.

## Tasks

### Setup Auth0

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, single page web application
4. Create a new API
   - in API Settings:
     - Enable RBAC
     - Enable Add Permissions in the Access Token
5. Create new API permissions:
   - `get:drinks`
   - `get:drinks-detail`
   - `post:drinks`
   - `patch:drinks`
   - `delete:drinks`
6. Create new roles for:
   - Barista
     - can `get:drinks-detail`
     - can `get:drinks`
   - Manager
     - can perform all actions
7. Test your endpoints with [Postman](https://getpostman.com).
   - Register 2 users - assign the Barista role to one and Manager role to the other.
   - Sign into each account and make note of the JWT.
   - Import the postman collection `./starter_code/backend/udacity-fsnd-udaspicelatte.postman_collection.json`
   - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, and including the JWT in the token field (you should have noted these JWTs).
   - Run the collection and correct any errors.
   - Export the collection overwriting the one we've included so that we have your proper JWTs during review!

### Implement The Server

There are `@TODO` comments throughout the `./backend/src`. We recommend tackling the files in order and from top to bottom:

1. `./src/auth/auth.py`
2. `./src/api.py`

### API Documentation

`GET '/api/v1.0/drinks

- Description: Fetches a dictionary of drinks where the keys are the drink IDs and the values are the       corresponding drink data.
- Request Arguments: None
- Returns: A JSON object with a single key, drinks, which contains an object mapping each drink ID to its corresponding data (e.g., title, recipe, etc.).

```json

"drinks": {
    "1": {
        "id": 1,
        "recipe": [
            {
                "color": "blue",
                "parts": 1
            }
        ],
        "title": "water"
    }
},

```
`GET '/api/v1.0/drinks-detail

- Description: Returns a dictionary of drinks where each key is a drink ID and the value is the corresponding drink object.
- Request Arguments: None
- Returns: An object with a single key, drinks, containing key-value pairs where each key is a drink ID and each value is an object with id, title, and recipe (an array of objects with name, color, and parts).

```json

"drinks": {
  "1": {
      "id": 1,
      "recipe": [
          {
              "color": "blue",
              "name": "water",
              "parts": 1
          }
      ],
      "title": "water"
  }
},

```
```
`POST '/api/v1.0/drinks

- Description: Creates a new drink and returns a list of created drinks. Each drink object contains its id, title, and recipe (an array of objects with name, color, and parts).
- Request Arguments: JSON object in the request body with the following fields:
    {
        "title":"Sunset",
        "recipe":[
            {"name":"Orange Juce","color":"orange","parts":2},
            {"name":"Tomato Juce","color":"red","parts":1},
            {"name":"Blubery juce","color":"purple","parts":3}
        ]
    }
- Returns: JSON object with a single key "drinks", containing a list of drink objects. Each object includes:
    id (integer) — auto-generated drink ID
    title (string) — drink name
    recipe (array) — array of ingredients as objects with name, color, and parts

```json

"drinks": [
    {
      "id": 1,
      "recipe": [
        {
          "color": "blue",
          "name": "water",
          "parts": 1
        }
      ],
      "title": "water"
    },
    {
      "id": 2,
      "recipe": [
        {
          "color": "grey",
          "name": "milk",
          "parts": 1
        },
        {
          "color": "green",
          "name": "matcha",
          "parts": 3
        }
      ],
      "title": "matcha shake"
    },
    {
      "id": 3,
      "recipe": [
        {
          "color": "orange",
          "name": "Orange Juce",
          "parts": 2
        },
        {
          "color": "red",
          "name": "Tomato Juce",
          "parts": 1
        },
        {
          "color": "purple",
          "name": "Blubery juce",
          "parts": 3
        }
      ],
      "title": "Sunset"
    }
],
```
```
`PATCH '/api/v1.0/drinks/{id}

- Description: Updates an existing drink by ID and returns the updated drink. Each drink object contains its id, title, and recipe (an array of objects with name, color, and parts).
- Request Arguments: 
    URL parameter: id (integer) — the ID of the drink to update
    JSON object in the request body with the following fields:
    {
    "recipe":[{"color":"lightgreen","name":"milk","parts":1},{"color":"green","name":"matcha","parts":3}],"title":"matcha shake"}
- Returns: JSON object with a single key "drinks", containing a list with the updated drink

```json

"drinks": {
        "id": 2,
        "recipe": [
            {
                "color": "lightgreen",
                "name": "milk",
                "parts": 1
            },
            {
                "color": "green",
                "name": "matcha",
                "parts": 3
            }
        ],
        "title": "matcha shake"
    },
```
`DELETE '/api/v1.0/drinks/{id}

- Description: Deletes an existing drink by ID and returns the ID of the deleted drink.
- Request Arguments: No body arguments are required.

- Returns: Returns: JSON object with:
    success (boolean) — indicates whether the deletion was successful
    delete (integer) — the ID of the deleted drink

```json

{
    "delete": 2,
    "success": true
}
```