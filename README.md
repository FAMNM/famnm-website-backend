# FAMNM Website Backend

This is the backend for [FAMNM's website](https://famnm.club).

## Tour

All commands should be run in the root directory of this repository unless otherwise stated. They might not work otherwise.

### Tools You Will Need

* [Git](https://git-scm.com)
* [Python 3](https://www.python.org/downloads/)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

Check if you have them installed:

```bash
git --version
python3 --version
heroku --version
```

### Setup Python Virtual Environment

Python virtual environments allow you to keep an installation packages specific to a project seperate from your global environment (and other virtual environments). [Full Documentation](https://docs.python.org/3/library/venv.html).

Create the virtual environment in the directory `venv/` (only needs to be done once):

```bash
python3 -m venv venv/
```

Activate the virtual environment (needs to be done for every shell you open):

```bash
source venv/bin/activate
```

Install packages listed in `requirements.txt` (needs to be done at the start and whenever the file changes):

```bash
pip3 install -r requirements.txt
```

Note: If you install any new packages (or uninstall existing ones), you *must* update `requirements.txt` to reflect these changes, otherwise other people and the web host won't be able to run the code. Please make these updates by hand, since using `pip3 freeze` can result in dependency hell.

### Login to and Setup Heroku CLI

This step is optional, and won't be possible unless you have access to the FAMNM Webmaster Heroku account.

Login:

```bash
heroku login
```

Connect your local repository to the application running on Heroku:

```bash
heroku git:remote --app famnm-website-backend
```

### Environmental Variables

You can put environmental variables in the `.env` file in the following format:

```.env
VARIABLE_NAME_1=value 1
VARIABLE_NAME_2=value 2
```

If you setup the Heroku CLI, you can copy the environmental variables that are currently being used on the deployed application to the end of your local `.env` file with the following command:

```bash
heroku config:get VARIABLE_NAME --shell >> .env
```

### Run Locally

The `flask` development server will also run with the environmental variables specified in `.flaskenv`. This means that it will automatically reload whenever you change any of the source code, and it will show an interactive debugger in the browser if an error occurs during a request. It is **not safe for production**.

Run the development server locally:

```bash
flask run
```

The `gunicorn` production server will run as it is defined in `Procfile`. The application should behave identically to how it does on the `flask` server, but in a way that's safe for production.

Run the production server locally:

```bash
heroku local web
```
