## Introduction

This application is a part of a Bachelor Thesis from MFF UK by Michaela Vystrcilova.

## Instalation

The installation guide is for a computer with a Linux operating system

### pre-requisities

* Linux operating system
* Python 3.5 or newer
* pip
* RabbitMQ
* postgreSQL database
* postresql-contrib
* libpq-dev
* see requirements.txt for the necessary Python packages

### Getting the application

Select a repository and clone the project using:

 `git clone git@github.com:Mvystrcilova/songRecommender.git`
 
### Set up the database
If you do not have postgres installed, run apt to get the packages you need:

`sudo apt-get update` 

`sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib`

Next create the database and the database user: 

`sudo su - postgres`

you should be in a shell session for the user `postgres`, run a Postgres session with typing `psql` into the command line

Now you need to create the database. The following database and user names and password are 
already specified in `songRecommender_projects.settings.py`
if you wish to change the names, you also need to change it in `songRecommender_projects.settings.py`.

create the database with typing the following command inside the Postgres session:

`CREATE DATABASE postgres;`

then create a user which will be interacting with the database

`CREATE USER postgres WITH PASSWORD 'password';`

change the encoding to UTF-8 which is expected by Django

`ALTER ROLE postgres SET client_encoding TO 'utf8';`

now, grant all access rights to the database user:

`GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;`

Exit the Postgres session using `\q` then exit the postgres user's shell session with `exit`.

### Setup the application

#### Important notes
After setting up the application as described in "Running the application", it will not be 
functional without the models. 
The models, distances and representation are not a part of the Git project because of their size.
They do not fit into SIS either but we saved the models to the Google disc drive and they can be found under this link [a link]
(https://drive.google.com/drive/folders/1Ejvj7_M3Dfi0a_qo8iHYu2LvaVf6Timx?usp=sharing). The models are expected to
be in the `songRecommender_project/models` directory, the representations in 
`songRecommender_project/representations` directory and the distances in the 
`songRecommender/distances` directory. The directories locations are described as the relative path from the 
root of the project.
 
 To load the songs representations and distances to the database, please uncomment 
`songRecommender.views.py` lines 104-106.

The mp3 files are also not a part of the Git project which means, that only songs added via the application 
after its ran will be playable. They are expected to be in the `mp3_files/mp3_files` directory.


It is necessary to download the models and place them into the correct directory in order for the application to run,
 they will be loaded into memory when starting the server.
 
 #### Running the application
Before starting the application, it is necessary to apply migrations to the database
with the following two commands in the projects root directory (the one where the `manage.py`
file is):

`python manage.py makemigrations`

`python manage.py migrate` 

Afterwards, you can run the application using:

`python manage.py runserver `

This will run the application on localhost and it can be viewed under `127.0.0.1:8000/index/`

To run also the `celery` task queue type the following into the terminal, also from the
projects root directory:

`celery worker -A songRecommender_project -l info --pool gevent`

Now everything if the models are present everything should be up and running. The representations and distances
are not necessary in order to run the application but 
the application will be empty without any songs upfront. Also, do not uncomment lines 104-106 if
representations and distances are not present.

## Developer documentation

For implementation details and high-level developer information, please see the thesis Chapter 5.

### Directory and module contents

#### Root 
The root of the project songRecommender_project contains:
 
 * `songRecommender` directory -- modules desribed in more detail below
 * `songRecommender_project` directory -- modules described in more detail below
 * `manage.py` from which the application is being run
 * `requirements.txt` describing the Python packages to run this application
 * `README.md` containing the application setup and installation
 * `docker-compose, Dockerfile` and `entrypoint.sh` which were used to handle the database and 
 provide the portability of the application without a server. Now they are not necessary as the application
 is running on a server
 
 It should also contain byt is not included in the Git project:
  * mp3_files with all the downloaded mp3 files for songs in the application

 
#### songRecommeder_project
The `songRecommender_project` directory contains:

* `__init.py__ ` in which the `celery` is imported
* `_celery` which contains `Celery` configurations 
* `not_empty_songs_relative_path.txt` in which the artist, 
title, lyrics, youtube link and the relative path to the mp3 file
for each of the base 16594 songs is included
* `settings.py` which includes the overall settings of the Django application
including the database, static file locations, templates, password handler, email handler,
the similarity method threshold, method models etc.
* `tasks.py` in which the method that are or can be called asynchronously by `celery` 
implemented. It includes most of the application's logic
* `urls.py` module configures the urls used for the songRecommender_project
* `useful_songs` which is a text file containing the titles and artists of the 16594 base songs
* the wsgi.py which exposes the WSGI


It also should contain but is not included in the Git project:

* `representations` directory in which the representations of songs in the implemented methods are stored
* `models` directory in which the models for the implemented methods are stored
* `distances` directory in which the distance matrices for the implemented methods are stored

#### songRecommender

The songRecommender directory contains:

* the `data` directory in which
   * the `load_distances.py` module contains methods used to load the
   16594 base songs, their representations and the distances between them into the database
   * the `prepare_songs_for_database` is a module that was used to get an mp3 file
   for each songs and also its path and is not useful in this version of the application
* the `Logic` directory in which
   * the `adding_songs.py` module contains key methods to handle the addition of a new song
   * the `Recommender.py` module contains one method that is no longer in use to change the url of a
   song added by a user into the application and a method that checks if a song was
   played by a user and recalculated distances accordingly
   * the `migrations` directory which contains auto-generated Django migration files
   * the `static` directory which contains static files used by the application
* the `templates` directory which contains the templates of all HTML pages
    * the templates that are in this directory or in the `registration` directory
       are used to handle sign up, log in and log out views
    * the templates in the `songRecommender` directory handle all the other pages
       of the web application
* `__init__.py` module which is empty and is auto generated by Django
* `admin.py` module where all database models are registered
* `apps.py` module which includes the names of the applications inside the `songRecommender_project`
project
* `forms.py` where all the forms for the applications are located
* `models.py` module in which the models corresponding to the database tables
are defined and their features and properties set
* `tests.py` is meant to contain tests but there are non for this application
* `tokens.py` module which generates the tokens for email authentication
* `urls.py` module which configures the urls for the songRecommender application
* `views.py` module that contains the implementation of all the views of this application 

### Additional remarks
In this state, it is difficult to implement a new method into the application and extensive
changes or better to say additions to the source code would have to be implemented in order to do so. 
Therefore a way possible future direction might be to ease this process and allow for easier new method
implementation.
