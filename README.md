# feature_req
demo app for flask, knockoutjs, json rest api

prepare PostgreSQL database
- createuser -d bc
- createdb feature_requests -O bc
- createdb feature_requests_test -O bc

to create schema and populate some data, enter python console:
```
$ python
from app import db
from app import Client, ProductArea, FeatureRequest
db.create_all()

db.session.add(Client('Client A'))
db.session.add(Client('Client B'))
db.session.add(Client('Client C'))

db.session.add(ProductArea('Policies'))
db.session.add(ProductArea('Billing'))
db.session.add(ProductArea('Claim'))
db.session.add(ProductArea('Reports'))

db.session.commit()
exit()
```
To run tests, from top folder ( with app.py), type
```
py.test
```
html5 input type 'date' used in template for target_date. Expected format is
yyyy-mm-dd for value, even if placeholder may show dd/mm/yyyy. I suggest to use
Chrome browser and input date by invoking built-in date-picker, nothing else was
done to ensure proper format.

