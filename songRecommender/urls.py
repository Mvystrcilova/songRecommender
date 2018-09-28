from django.urls import path
from songRecommender import views


urlpatterns = [
    path('index/', views.HomePageView.as_view(), name='index')

]