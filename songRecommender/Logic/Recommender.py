from songRecommender.models import Song, List, Distance, User, Distance_to_User, Distance_to_List, Played_Song
# from songRecommender.Logic.model_distances_calculator import save_user_distances, save_list_distances
from songRecommender_project.tasks import recalculate_all_distances_to_user
import re


def check_if_in_played(song_id, cur_user, is_being_played):
    """checks if the song was already played by the user, if not it adds it
    and if yes and it is being played again the number of times played is updated accordingly"""

    song = Song.objects.get(id=song_id)

    if song.pk in Played_Song.objects.filter(user_id=cur_user.profile).values_list('song_id1_id', flat=True):
        if is_being_played:
            played_song = Played_Song.objects.get(user_id=cur_user.profile, song_id1=song)
            played_song.numOfTimesPlayed += 1
            played_song.save()

    else:
        played_song = Played_Song(user_id=cur_user.profile, song_id1=song, opinion=0, numOfTimesPlayed=1)
        played_song.save()
        recalculate_all_distances_to_user.delay(song_id, cur_user.pk)

    return


def change_youtube_url(url):
    """takes the youtube url from either the address bar
     or the one from the share option under the Youtube video
     and changes it to an embedable one"""

    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return "https://www.youtube.com/embed/" + youtube_regex_match.group(6)

    return youtube_regex_match
