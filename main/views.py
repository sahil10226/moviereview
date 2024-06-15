import requests
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from .forms import *
from django.db.models import Avg
from django.conf import settings

# Create your views here.
def home(request):
    query = request.GET.get("title")
    allMovies = None
    if query:
        # If query exists, fetch movies from TMDB API
        url = f"{settings.TMDB_API_BASE_URL}/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            allMovies = data.get('results', [])
            # Map TMDB fields to your model fields
            for movie in allMovies:
                movie['name'] = movie.pop('title')
                movie['description'] = movie.pop('overview')
    else:
        # If no query, fetch popular movies from TMDB API
        url = f"{settings.TMDB_API_BASE_URL}/movie/popular?api_key={settings.TMDB_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            allMovies = data.get('results', [])
            # Map TMDB fields to your model fields
            for movie in allMovies:
                movie['name'] = movie.pop('title')
                movie['description'] = movie.pop('overview')
        else:
            allMovies = Movie.objects.all()  # Fallback to database if API fails
     
    context = {
        "movies" : allMovies,
    }
    
    return render(request, 'main/index.html',context)

#detail page

def detail(request, id):
    # Fetch movie details from TMDB API
    movie_url = f"{settings.TMDB_API_BASE_URL}/movie/{id}?api_key={settings.TMDB_API_KEY}"
    cast_url = f"{settings.TMDB_API_BASE_URL}/movie/{id}/credits?api_key={settings.TMDB_API_KEY}"
    
    movie_response = requests.get(movie_url)
    cast_response = requests.get(cast_url)
    
    movie = None
    cast = None
    
    if movie_response.status_code == 200:
        movie = movie_response.json()
    
    if cast_response.status_code == 200:
        cast = cast_response.json().get('cast', [])
    
    # Fetch reviews for the movie
    reviews = Review.objects.filter(movie=id).order_by("-comment")
    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average is None:
        average = 0
    average = round(average, 2)
    
    context = {
        "movie": movie,
        "cast": cast,
        "reviews": reviews,
        "average": average
    }

    return render(request, 'main/details.html', context)

# Add movies

def add_movies(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == "POST":
                form = MovieForm(request.POST or None)

                if form.is_valid():
                    data = form.save(commit=False)
                    data.save()
                    return redirect("main:home")
            else:
                form = MovieForm()
            return render(request, 'main/addmovies.html', {"form": form, "controller": "Add Movies"})
        else:
            return redirect("main:home")
        
    return redirect("accounts:login")

def add_review(request, id):
    if request.user.is_authenticated:
        try:
            movie = Movie.objects.get(id=id)
        except Movie.DoesNotExist: 
            url = f"https://api.themoviedb.org/3/movie/{id}?api_key=d90ca939adaa08383d9f3b40d23ecbc8"
            response = requests.get(url)
            if response.status_code == 200:
                tmdb_movie = response.json()
                movie = Movie(
                    id=id,
                    name=tmdb_movie['title'],
                    description=tmdb_movie['overview'],
                    release_date=tmdb_movie['release_date'],  # Populate release_date if available
                    image=f"https://image.tmdb.org/t/p/w500{tmdb_movie['poster_path']}"
                )
                movie.save()  # Save movie to local DB for future use
            else:
                return redirect("main:home")

        if request.method == "POST":
            form = ReviewForm(request.POST or None)
            if form.is_valid():
                data = form.save(commit=False)
                data.comment = request.POST["comment"]
                data.rating = request.POST["rating"]
                data.user = request.user
                data.movie = movie
                data.save()
                return redirect("main:detail", id)
        else:
            form = ReviewForm()
        return render(request, 'main/details.html', {"form": form, "movie": movie})  # Highlighted: Pass movie to context
    else:
        return redirect("accounts:login")
    
def edit_review(request, movie_id, review_id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=movie_id)

        review = Review.objects.get(movie=movie, id=review_id)

        if request.user == review.user:
        
            if request.method == "POST":
                form = ReviewForm(request.POST, instance=review)
                if form.is_valid():
                    data = form.save(commit=False)
                    if (data.rating > 10) or (data.rating < 0):
                        error = "Out of Range. PLease select rating from 0 to 10."
                        return render(request, 'main/editreview.html', {"error":error, "form":form})
                    else:
                        data.save()
                        return redirect("main:detail", movie_id)
            else:
                form = ReviewForm(instance=review)
            return render(request, 'main/editreview.html', {"form": form})
        else:
            return redirect("main:detail",movie_id)
    else:
        return redirect("accounts:login")
    
def delete_review(request, movie_id, review_id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=movie_id)

        review = Review.objects.get(movie=movie, id=review_id)

        if request.user == review.user:
            review.delete()

        return redirect("main:detail",movie_id)
    else:
        return redirect("accounts:login")