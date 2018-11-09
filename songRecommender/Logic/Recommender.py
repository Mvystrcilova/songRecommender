from songRecommender.models import Song, Distance, User, Distance_to_User, Distance_to_List, Played_Song


# checks if the song was already played by the user, if not it adds it
# and if yes and it is being played again the number of times played is updated accordingly
def check_if_in_played(song_id, cur_user, is_being_played):
    song = Song.objects.get(id=song_id)

    if song in Played_Song.objects.filter(user_id=cur_user).values_list('song_id1'):
        if is_being_played:
            played_song = Played_Song.objects.get(user_id=cur_user, song_id1=song)
            played_song.numOfTimesPlayed += 1
            played_song.save()

    else:
        played_song = Played_Song(user_id=cur_user, song_id1=song, opinion=0, numOfTimesPlayed=1)
        played_song.save()

    return

