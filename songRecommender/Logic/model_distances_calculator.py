from songRecommender.models import Song, Distance, Distance_to_List, Distance_to_User, Played_Song, Song_in_List


def save_user_distances(added_song, cur_user, distance_type):
    """calculates the distance of the given song to every user in database
    if the distance already exists it updates it otherwise it creates it
    the user it gets is an instance of user and NOT profile"""

    all_songs = Song.objects.all().order_by('-id')  # gets all songs from database
    played_songs = Played_Song.objects.all().filter(user_id_id=cur_user.profile.pk)  # gets all the users played songs

    counter = 0
    user_to_song_distance = 0

    # for every song in the database if it is not the added song and the user played the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in played_songs.values_list('song_id1_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song, user_id_id=cur_user.profile.pk)

            if the_song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                    distance_Type=distance_type).distance
                except:
                    the_distance = 0

                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                user_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk, user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': user_to_song_distance / counter})
    else:
        distance_to_user, created = Distance_to_User.objects.update_or_create(song_id_id=added_song.pk, user_id_id=cur_user.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': 0})
    distance_to_user.save()

    return


def save_list_distances(added_song, the_list, cur_user, distance_type):
    """saves the distance of given song to the given list into the database
    the cur_user it gets is and instance of user and NOT Profile"""

    all_songs = Song.objects.all().order_by('-id')
    songs_from_list = Song_in_List.objects.filter(list_id=the_list)

    counter = 0
    list_to_song_distance = 0

    # for every song in the database if it is not the added song and the list contains the song, it adds the distance
    # the higher the distance the closer is the song
    for song in all_songs:
        if (song.pk != added_song.pk) and (song.pk in songs_from_list.values_list('song_id_id', flat=True)):

            the_song = Played_Song.objects.get(song_id1=song, user_id_id=cur_user.profile.pk)

            if the_song.opinion != -1:
                try:
                    the_distance = Distance.objects.get(song_1=song, song_2=added_song,
                                                        distance_Type=distance_type).distance
                except:
                    the_distance = 0
                num_of_times_played = the_song.numOfTimesPlayed

                # the distance is multiplied by the number of times the user played the song
                # also if the user likes the song, one more distance is added, if he does not the second part is 0
                list_to_song_distance += the_distance * num_of_times_played + the_distance * the_song.opinion
                counter += 1

    if counter != 0:
        distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
                                                                              list_id_id=the_list.pk,
                                                                              distance_Type=distance_type,
                                                                 defaults={'distance': list_to_song_distance / counter})

    else:
        distance_to_list, created = Distance_to_List.objects.update_or_create(song_id_id=added_song.pk,
                                                                              list_id_id=the_list.pk,
                                                                              distance_Type=distance_type,
                                                                              defaults={'distance': 0})

    distance_to_list.save()

    return
