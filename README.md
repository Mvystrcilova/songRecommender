Popis:

Soubory ktere jsem psala:
models.py
    navrh databaze, modely
    
urls.py
    url ktere to matchuje
views.py
    class-generated views, ktere predavaji informace do html souboru
    
songRecommender/urls.py

templates
    base_generic - template pro vsechny ostatni
    jinak kazdy html soubor na jednu tu stranku ze specifikace
    
Logic/Tf-idf
    algoritmus na pocitani vzdalenosti pisnicek pomoci TF-idf, pro pisnicky uz spocitane
    
Logic/document-similarity-master/data
       algoritmus pou6ivajici predtrenovany Google W2V model na urcovani vzdalenosti souboru
       
To Do - programovaci:
     Najit youtube linky k jednotlivym skladbam  
     Odhlasit pri odhlaseni
     Nedoporucovat pisnicky, ktere uz uzivatel prehral nebo ma v danem listu
     Udelat stranku se vsemi pisnickami - skoro hotovo
     Udelat vyhledavani
     Trochu omezit co lze pridat
     Regexovat youtube linky - hotovo
     Delat si ucty + maily - hotovo
     Dat moznost aby se pisnicka libila - hotovo
     dat moznost pridat pisnicku do listu -  hotovo
     prepocitat vzdalenost pri pridani pisnicky - hotovo
     Urcit koeficienty pro podobnost a skladat jednotlive vzdalenosti - hotovo
 
 TO DO - neprogramovaci:
    Okomentovat kod
    Vytvorit dokumentaci strojovou
    vytvorit dokumentaci programatorskou
    udelat balicek
