# SnookR
Copyright &copy; 2017 Evan Smelser

An open source webapp facilitating communication amongst pool players built in Python using Django

Work In Progress.

## Project Setup

SnookR was designed and written with Python 3.52, that will be specified in the creation of your
virtual environment.

### Clone the repo

```
git clone https://github.com/eSmelser/SnookR.git
```

Once cloned, go ahead and change into the main project directory

```
cd SnookR/SnookR
```

### Create virtual env

If you are using [Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) (and you should be)

```
mkvirtualenv SnookR
```
This will automatically activate your virtual environment `SnookR`

without virtualenvwrapper

```
virtualenv -p path/to/python3 SnookR
. SnookR/bin/activate
```

### Use Pip to install Requirements

You should, of course, have the correct version of pip installed corresponding to Python3

```
pip install -r requirements.txt
```

## How to Setup your local instance

### Use Python and manage.py to make database migrations

```
python manage.py migrate
```

### Use Python and manage.py to run custom test data population script to add test data to your db

```
python manage.py db_populate
```

### Use Python and manage.py to locally serve SnookR

```
python manage.py runserver
```

Then simply navigate to the home page of the specified URL by the runserver output ex. `http://127.0.0.1:8000/home`

## How to use

### Click on one of the sign-up links to create a user

Once you sign up as a user in the system, a player object will automatically be created for you and linked to your user so that you can register for sublists.

### Navigate to currently available Divisions

Once logged in, you have access to the Divisions list. Click on the `Divisions` tab in the header to be taken to a list of divisions

### Select a Session

Select a session within a division to be taken to a list of players registered to sub in that division during the selected session.
From here you will have the options to register/unregister to sub during that session on a particular date that you are available.

### Back to Home

Once you register to sub for a division during a particular session, you will be redirected back to your home page, and you will be able to see all of the sublists you are currently related to.


## Notes

### 8/18/2017

* At this point, the primary focus is on functionality. Getting a functional sublist setup so that players and teams can login and register to sub in BCA pool divisions. Thus, SnookR is not yet **pretty**.
* The sublist app within SnookR may soon be deprecated. We were able to add the necessary functionality with just the models in the main app, however there is current discussion to see which is the right way to go.
* The current focus is on getting Teams up and running so that players can create teams within divisions and all the appropriate data connections and links will be made within the app.
* Then the month of September will be spent getting the app to look **pretty** as we would like it to be presentable as a demo to the local Western BCA league operators by October 1, 2017.

## KanBan Board

* [SnookR Tracking](https://trello.com/b/Rrb3Ud76) - A Trello Board containing the current status of work on SnookR

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used

## Authors

* **Evan Smelser** - *Initial work* - [SnookR](https://github.com/esmelser/SnookR)
* **Bobby Eshleman** - *Initial work* - [SnookR](https://github.com/esmelser/SnookR)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Limitations

* Currently a work in progress - Not yet fully functional, Pilot: Version 1.0.0 goal October 1, 2017
* Please see Github [Issues](https://github.com/esmelser/SnookR/issues) for a list of current issues


