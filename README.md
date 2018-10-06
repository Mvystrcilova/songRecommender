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
       
ToDo:
    Dodelat vsechny html
    Propojit views s templatama
    Napsat funkce na handlovani Http requestu
    Najit youtube linky k jednotlivym skladbam     
 
