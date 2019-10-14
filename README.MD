Django web app for fetching and storing movies data from http://www.omdbapi.com/

#### To run locally:
1. Set OMDB_API_KEY=... in `.local_env` file in main directory.
    - get api key from http://www.omdbapi.com/
1. Run following commands:
    ```
    pip install -r requirements-dev.txt
    docker-compose build
    docker-compose up
    ```

#### To run tests:
1. Run following commands:
    ```
    pip install -r requirements-dev.txt
    docker-compose -f docker-compose.test.yml build
    docker-compose -f docker-compose.test.yml up --abort-on-container-exit
    ```
#### To deploy:

1. Make an account on Heroku, create a new pipeline - please refer to official article on [Heroku's Website](https://devcenter.heroku.com/articles/pipelines)
1. Mandatory environment variables in Heroku are:
    - APPLICATION_ENVIRONMENT=prod
    - DATABASE_URL (generated automatically upon adding [postgresql add-on in Heroku](https://elements.heroku.com/addons/heroku-postgresql))
    - HOSTNAME - domain on which the site will be hosted, for example <app_name>.herokuapp.com
    - SECRET_KEY - [django secret key](https://docs.djangoproject.com/en/2.2/topics/signing/#protecting-the-secret-key)
    - OMDB_API_KEY - get from http://www.omdbapi.com/
    - DISABLE_COLLECTSTATIC=1
1. Install [heroku-cli](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
1. Install **container-registry** plugin
    ```
   heroku plugins:install @heroku-cli/plugin-container-registry
    ```
1. Push and release to your app:
    ```
   heroku container:push web -a <app_name>
   heroku container:release -a <app_name> web
   heroku run -a <app_name> bash migrate_prod.sh
    ```
   
#### Exposed endpoints:

##### /movies

GET query parameters:
1. order - order results by movie data, prepend "-" for descending sorting, parameter name must have matching case
1. search - search within following fields: `Title` `Director` `Writer` `Actors` `Production`
1. year - filter results by year
1. page - used for pagination, default is 1

examples:
```
    /movies?order=-Year
    /movies?search=Tarantino
    /movies?year=2018&page=2 
```
response:
```
    {
        "results": [
            {
                "id": 1,
                ... (other attributes vary depending on each entry, for example if it's a series they might include number of seasons)
            },
            {
                "id": 2,
                ...
            },
            ...
        ]
    }
```

POST attributes:
1. title - title of a movie or series, this is mandatory

example payload:
```
    {
        "title": "Pirates of the Caribbean"
    } 
```

example response:
```
    {
       "id":17,
       "Title":"Pirates of the Caribbean: The Curse of the Black Pearl",
       "Year":"2003",
       "Rated":"PG-13",
       "Released":"09 Jul 2003",
       "Runtime":"143 min",
       "Genre":"Action, Adventure, Fantasy",
       ...
    }    
```

##### /comments

GET query parameters:
1. movie - id of movie
1. page - used for pagination, default is 1

examples:
```
    /comments?movie=5
    /comments?page=2 
```

example response:
```
{ 
   "results":[ 
      { 
         "movie_id":1,
         "comment":"Ok",
         "added_on":"2019-10-16T21:23:33.347816+00:00",
         "id":1
      },
      ...
      { 
         "movie_id":1,
         "comment":"Awesome",
         "added_on":"2019-10-16T21:24:01.957353+00:00",
         "id":6
      },
      { 
         "movie_id":2,
         "comment":"Decent.",
         "added_on":"2019-10-16T21:24:24.348846+00:00",
         "id":10
      }
      ...
   ]
}
```

POST attributes:
1. movie - movie id
1. comment - text

example payload:
```
{
        "movie_id": 1,
        "comment": "Fun",
}
```

example response:
```
    {
        "movie_id": 1,
        "comment": "Fun",
        "added_on": "2019-10-16T21:26:16.853411+00:00"
        "id":28
    }
```

##### /top

GET query parameters:
1. from - from datetime (ISO 8601-compatible, only UTC is supported)
1. to - to datetime (ISO 8601-compatible, only UTC is supported)

examples:
```
/top?from=2019-10-12&to=2019-10-20T20:00:00
```

example response:
```
    {
       "results":[
          {
             "movie_id":2,
             "rank":1,
             "total_comments":12
          },
          {
             "movie_id":1,
             "rank":2,
             "total_comments":8
          },
          {
             "movie_id":3,
             "rank":3,
             "total_comments":4
          },
          {
             "movie_id":4,
             "rank":3,
             "total_comments":4
          }
       ]
    }
```