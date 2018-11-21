
      
## Setup

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

## Recomendation techniques

Right now, there are two possible recommendation techniques that can be used in this application
that have pre-trained models in place and can be used without the need of training or supplying
special data

### TF-idf
the TF-idf is not only pre-trained already but data and similarity values are already inside the database
and all potential users have access to them
* adding data
    * the data can be

### Word2Vec
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
