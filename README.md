
      
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
 
## To Do - programovaci:
* zkontrolovat jestli u vsech played songs je to profile.pk a ne user.pk
* poresit to, kdyz uzivatel dislikne pisnicku aby ji nasel jen pri vylozene vyhledavani
* Nedoporucovat pisnicky, ktere uz uzivatel prehral nebo ma v danem listu - hotovo
* Najit youtube linky k jednotlivym skladbam - uz vim jak, ale problem
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
* Okomentovat kod
* Vytvorit dokumentaci strojovou
* vytvorit dokumentaci programatorskou
* udelat balicek - hotovo
