# SnookR
Copyright &copy; 2017 Evan Smelser

An open source webapp facilitating communication amongst pool players built in Python using Django

Work In Progress.

## Project Progress

### Week 1

* Research and consider reasonable MVP
* Watch pluralsight Python Videos
* Create [Trello](https://trello.com/b/Rrb3Ud76) board to keep track of current status of project
* Held meetings with a few acquaintances for project and tool guidance 

### Week 2

* Work through Python Koans to help learn Python Basics
* Watch pluralsight video on Django basics
* Met with friend David who runs local divisions of BCA Billiards league. He is interested in possible
   sponsorship, working on using the project developed in this class as a demo for him and his
   compatriots.

### Week 3

* Shared project idea with a friend and he agreed to assist/collaborate on project moving forward
* Worked out VirtualEnv and installed Django in app
* Worked through Django Pluralsight demo "Hello World" application to get a Django hello world app up
   and running, although that is not a part of this project.
* Created slack channel for project collaboration
* Set up Django App for sublists
* Add Views for each of the various divisions for their respective sublists
* Add HTML Templates for each of the sublists

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


## KanBan Board

* [SnookR Tracking](https://trello.com/b/Rrb3Ud76) - A Trello Board containing the current status of work on SnookR

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used

## Authors

* **Evan Smelser** - *Initial work* - [SnookR](https://github.com/esmelser/SnookR)

See also the list of [contributors](https://github.com/esmelser/SnookR/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments


