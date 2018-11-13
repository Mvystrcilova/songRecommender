from songRecommender.models import Song, Distance, Distance_to_List, Distance_to_User, Played_Song, Song_in_List


# calculates the distance of the given song to every user in database

def save_user_distances(added_song, cur_user, distance_type):
    all_songs = Song.objects.all().order_by('-id')  # gets all songs from database
    played_songs = Played_Song.objects.all().filter(user_id_id=cur_user.profile.pk)  # gets all the users played songs

    counter = 0
    user_to_song_distance = 0

    # for every song in the database if it is not the added song and the user played the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in played_songs.values_list('song_id1_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song)

            if the_song.opinion != -1:
                the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                    distance_Type=distance_type).distance
                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                user_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_user = Distance_to_User(distance=user_to_song_distance / counter, distance_Type=distance_type,
                                        song_id_id=added_song.pk, user_id_id=cur_user.pk)
    else:
        distance_to_user = Distance_to_User(0, distance_Type=distance_type,
                                            song_id_id=added_song.pk, user_id_id=cur_user.pk)
    distance_to_user.save()

    return


# calculates the distance of given song to every list in the database
def save_list_distances(added_song, the_list, cur_user, distance_type):
    all_songs = Song.objects.all().order_by('-id')
    songs_from_list = Song_in_List.objects.filter(list_id=the_list)

    counter = 0
    list_to_song_distance = 0

    # for every song in the database if it is not the added song and the list contains the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in songs_from_list.values_list('song_id_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song, user_id=cur_user.profile)

            if the_song.opinion != -1:
                the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                    distance_Type=distance_type).distance
                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                list_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_list = Distance_to_List(distance=list_to_song_distance / counter, distance_Type=distance_type,
                                        song_id_id=added_song.pk, list_id_id=the_list.pk)
    else:
        distance_to_list = Distance_to_List(0, distance_Type=distance_type,
                                            song_id_id=added_song.pk, list_id_id=the_list.pk)

    distance_to_list.save()

    return
