# FAMNM Website Backend

This is the backend for [FAMNM's website](https://famnm.club).

All commands in this guide should be run in the root directory of this repository unless otherwise stated. They might not work otherwise.

## Tools You Will Need

* [Git](https://git-scm.com/downloads)
* [Python 3](https://www.python.org/downloads/)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
* [PostgreSQL](https://www.postgresql.org/download/)

Check if you have them installed:

```bash
git --version
python3 --version
heroku --version
psql --version
```

## Setup Python Virtual Environment

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

## Login to and Setup Heroku CLI

This step is optional, and won't be possible unless you have access to the FAMNM Webmaster Heroku account. But if you don't do it, most of the subsequent `heroku` commands won't work.

Login:

```bash
heroku login
```

Connect your local repository to the application running on Heroku:

```bash
heroku git:remote --app famnm-website-backend
```

## Setup Database

### Local Database

Since the application interacts with a database, you will have to set up a test database if you wish to run the application locally.

Create a new local database called `famnm-test-db`:

```bash
createdb famnm-test-db
```

Initialize the local database with the correct tables:

```bash
psql famnm-test-db < initialize.sql
```

Now set the `DATABASE_URL` environmental variable to `postgresql://localhost/famnm-test-db` to tell the locally running application where is can find the database. See [the section on environmental variables](#environmental-variables) for how to do this easily.

You can access the PostgreSQL interactive terminal of the local database with the following command:

```bash
psql famnm-test-db
```

### Deployed Database

The deployed database should already exist and be initialized. If it isn't, you can make it so with the following commands:

Create the deployed database:

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

Initialize the deployed database with the correct tables:

```bash
heroku pg:psql < initialize.sql
```

Heroku will automatically set `DATABASE_URL` for you in the config variables of the deployed application. Do not attempt to set it manually, because the actual URL may change without notice.

You can access the PostgreSQL interactive terminal of the deployed database with the following command:

```bash
heroku pg:psql
```

## Environmental Variables

For local development, you can set environmental variables by making a `.env` file in the following format:

```.env
VARIABLE_NAME_1=value 1
VARIABLE_NAME_2=value 2
```

For the deployed application, config variables can be set using the following command:

```bash
heroku config:set 'VARIABLE_NAME_1=value 1' 'VARIABLE_NAME_2=value 2'
```

You can copy the config variables that are currently being used on the deployed application to the end of your local `.env` file with the following command:

```bash
heroku config:get VARIABLE_NAME --shell >> .env
```

## Run Locally

The `flask` development server will automatically reload whenever you change any of the source code, and it will show an interactive debugger in the browser if an error occurs during a request. It does this because of the additional variables set in `.flaskenv`. It is **not safe for production**.

Run the development server locally:

```bash
flask run
```

The `gunicorn` production server should behave identically to how it does on the `flask` server, but in a way that's safe for production. It is defined in the Heroku `Procfile` as what should be run when the application is deployed, which means that the following command will do the same thing, but locally.

Run the production server locally:

```bash
heroku local web
```

## Deploying

The application on Heroku is configured to automatically redeploy every time something new is added to the `master` branch on GitHub.

Any packages listed in `requirements.txt` will be installed, then the application will be run with the command(s) specified in `Procfile`.
