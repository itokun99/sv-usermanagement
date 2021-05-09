# SV Usermanagement

Microservice test with Python and Mysql

### how to run

```
#create venv
python3 -m venv venv

#active venv
. venv/bin/activate

#install package
pip install -r requirements.txt

#export variable
export FLASK_ENV=development
export FLASK_APP=main.py

# run server
flask run
```

### Database Setup

```
# change here
app.config["SQLALCHEMY_DATABASE_URI"] =  "mysql+mysqlconnector://root:root@localhost:8889/sv_usermanagement"

or create manually in mysql
```

## Postman

posmant: <https://documenter.getpostman.com/view/8214376/TzRRE9QN#introduction>

Any question ? please contact me on email
