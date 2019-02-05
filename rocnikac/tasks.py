from celery import Celery
from songRecommender.models import Song, List
from songRecommender.Logic.model_distances_calculator import save_list_distances, save_user_distances

app = Celery('tasks', broker='amqp://localhost')

@app.task
def add(x, y):
    print(x+y)
    return x + y

@app.task
def recalculate_distances(request, distance_type):
    """for every song in the database it recalculates
    the distance to every user and the distance to every list
    the current user has created"""

    songs = Song.objects.all()
    lists = List.objects.all().filter(user_id_id=request.user.id)

    for song in songs:
        save_user_distances(song, request.user, distance_type)

        for l in lists:
            save_list_distances(song, l, request.user, distance_type)
