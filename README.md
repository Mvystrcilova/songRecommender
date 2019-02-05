
##To Do Bakalarka

* zistit informace o datasetu
** mean songs per user
	3.56
** mean users per song
	10.84	
** number of users
	45054
** number of songs
	14 800


      
## Setupu

Application setup is done via environment variables.

* `DB_USER` - database user (default: `postgres`)
* `DB_NAME` - database name (default: `postgres`)
* `DB_PASSWORD` - database password (default: `password`)
* `DB_HOST` - database host (default: `127.0.0.1`)

## Develop

Run `pipenv install` command before developing and debugging.

## Deploy

### pre-requisities

You need to have `docker` and `docker-compose` installed to deploy
containerized application.

## Developer documentation

The application consists of two main parts. The first part is the application,
views, models and html pages.

The second part are recommendation techniques used. This part has potential to be extended and many different techniques can be implemented and used

### Application details

In this application all calculations are made on the server side. The client only sees HTML5 pages with some CSS for graphical design. The server side is written in the Django framework using Python 3.7. and the database POSTGRESQL is being handled by Docker. It can only be installed on a computer with `docker` and `docker-compose` because of the lack of a server where it could run.

### Application details

#### Client

The client has access to multiple html pages, all except of sign-up upon login. The html pages `add_song_failed.html`, `add_to_list_failed.html`, `addSong.html`, `all_songs.html`, `index.html`, `list_confirm_delete.html`, `list_detail.html'`, `list_form.html`, `my_lists.html`, `recommended_songs.html`, `search_results.html`, `song_detail.html` these handle most of the interaction with the user and in-application functionalities.
There are also special pages handling the user login and account `logged_out.html`, `login.html`, `password_reset_complete.html`, `password_reset_confirm.html`, `password_reset_done.html`,`password_reset_email.html`, `password_reset_form.html`, `account_activation_email.html`, `account_activation_sent.html`, `signup.html`.

The page `base_generic.html` is a base for all the html pages to keep the design consistent.

### The server

The server takes care of all the computation. Now the server does all computation on request of the user as he runs in one infinite loop waiting for a request. For future improvement when the ammont of data rises, it will be neccessary to do the caclulations in a new thread and let the user continue. This should not be a big of a problem since the database can be altered by users any time and it would not result in unconsistency of other data, the calculations and new entries wouldjust appear after a different request.

### Models

For every table in the database, there is a model in the module `models.py` specifying their features. There is a class for `song`, `list`, `profile` which is an extension of the build-in `user` class to enable specifiying the distance of songs to the user and also checking if the user has confirmed his email.

The class `Song in list` keeps track of lists and songs that belong together, the model `played song` specifies a user and all the songs he has played. One cannot unplay a song but it can be disliked so it would not appear anymore.

There are three different distance classes. First basic `distance` is the only class that actualy stores distance based on a calculation of a machine-learning algorithm. The classes `distance_to_user` and `distance_to_list` then calculate their distance data based on what they find in the `distance` table using an algorithm from the module `text_shaper.py`.

### Views

Views are the controller part of this application. They manage most of the data collection and send them to the html pages. 

There is one view for basicaly every html page plus some extra for some build in features for example liking and disliking songs.

The `HomePageView`, `MyListsView`, `AllSongsView`and `RecommendedSongsView` are build in Django list views with special features displaying querysets from the database. As the names suggest they dislay the homepage, all songs, songs recommended to the logged in user, and lists created by the logged in user.

The `ListDetailView` and `SongDetailView` are also Django build in views, for displaying detail pages of models from the database. They take care of displaying the detail page of a song and a list.

For the list, the creation, updating and deletion is also beign handled by build in views `ListUpdate`, `ListCreate` and `ListDelete`.

The rest is function based views corresponding each to some feature of the web application. The `like` and `dislike` views manage liking and disliking songs. Although there is a possibility to re-calculate everything when the user does this, it is not currently possible because of the speed and will need to be resolved in a different thread.

The add song view handles addding songs to the database. This can be done by any logged in user and it resulst into calculation all distances between the added song and all in the database and can take up tens of seconds.

The views `add_song_failed` handels if the user is trying to add a song that is probably already in the database.

The `signup, activate, account_activation_sent` and `logout` view hande user creation and authentification.

The last two are `add_sojng_to_list` and `add_to_list_failed` which handle adding songs to lists.

## Logic

### Recomendation techniques

Right now, there are two possible recommendation techniques that can be used in this application
that have pre-trained models in place and can be used without the need of training or supplying
special data

#### TF-idf
the TF-idf is not only pre-trained already but data and similarity values are already inside the database
and all potential users have access to them
if there is a distance missing the songs are thought to be completely different.
* adding data
    * the data can be

#### Word2Vec
the W2V model used here is a pre-trained google model https://code.google.com/archive/p/word2vec/
but only the 200 000 most used words.
This can be changed by de-commenting this code
```python
from gensim.models.keyedvectors import KeyedVectors

model_path = 'songRecommender/Logic/GoogleNews-vectors-negative300.bin'
w2v_model = KeyedVectors.load_word2vec_format(model_path, binary=True, limit=200000)
w2v_model.save('w2v_subset')
```
changing or deleting the limit parameter
then comment the code again and load the new model with the following command:
```python
from gensim.models.keyedvectors import KeyedVectors

w2v_model = KeyedVectors.load('w2v_subset', mmap='r')

``` 

the model will always be loaded when server is starting


right now, there is no data defining similarity between songs based on the W2V model but if all
TF-idf distances are disabled, the W2V will work calculating distances

The distance for W2V is calculated in the `DocSim.py` module.

#### Distance calculation

all methods to calculate distance between songs are in the `text_shaper.py` module. More can be added and all can be saved to the database using the `save_distance` method.

The module `Recommender.py` contains method that check and alter data in the database, also do collective recalculations that take a lot of time.

The `model_distance_calculator` implements methods that calculate the distance of a song to a particular user or list. These are also not dependent on the distance type they receive as a parameter and therefore can be used for any machine-learining algorithm. The idea is also that they should be used as that would keep the consinstency in results and make it easier for the algorithms to be compared and assesed.

## Data

There is a need to load a lot of data into the database. The user can alter the database by adding songs, creating lists and accounts. To add data on a bigger scale for all the users there are some scrips in the `data` directory, however they are quite specific for the data I accuired and submitted to the database.
 
## To Do - programovaci:
* zkontrolovat jestli u vsech played songs je to profile.pk a ne user.pk
* poresit to, kdyz uzivatel dislikne pisnicku aby ji nasel jen pri vylozene vyhledavani - hotovo
* Nedoporucovat pisnicky, ktere uz uzivatel prehral nebo ma v danem listu - hotovo
* Najit youtube linky k jednotlivym skladbam - v procesu
* Udelat aby se nedala pridat dvakrat stejna pisnicka do list - hotovo
* Udelat aby se nedala pridat dvakrat stejna pisnicka do databaze - hotovo
* Odhlasit pri odhlaseni - hotovo
* Udelat stranku se vsemi pisnickami - hotovo
* Udelat vyhledavani - hotovo
* Regexovat youtube linky - hotovo
* Delat si ucty + maily - hotovo
* Dat moznost aby se pisnicka libila - hotovo
* dat moznost pridat pisnicku do listu -  hotovo
* prepocitat vzdalenost pri pridani pisnicky - hotovo
* Urcit koeficienty pro podobnost a skladat jednotlive vzdalenosti - hotovo
 
## TO DO - neprogramovaci:
* Okomentovat kod - hotovo'
* Vytvorit dokumentaci strojovou 
* vytvorit dokumentaci programatorskou
* udelat balicek - hotovo
