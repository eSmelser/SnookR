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

### Create virtual env

If you are using [Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) (and you should be)

```
mkvirtualenv virtualenv_name
```
This will automatically activate your virtual environmtne `virtualenv_name`

without virtualenvwrapper

```
virtualenv -p path/to/python3 virtualenv_name
. virtualenv_name/bin/activate
```

### Use Pip to install Requirements

You should, of course, have the correct version of pip installed corresponding to Python3

```
pip install -r SnookR/requirements.txt
```

## How to use

### Use Python and manage.py to make database migrations

```
python manage.py makemigrations
python manage.py migrate
```

### Use Python and manage.py to locally serve SnookR

```
python manage.py runserver
```

### Navigate to the specified URL by the runserver output



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


