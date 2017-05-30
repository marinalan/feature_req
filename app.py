from flask import Flask, render_template, request, jsonify, abort, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.inspection import inspect
import json
import datetime

from flask.ext.heroku import Heroku

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://bc:ThieNg4qui@localhost/feature_requests'
#app.config['DEBUG']=True
app.config['SECRET_KEY']='\xf5\xaa\x1bt\xce3\x85q\xf0S\x1b\x91\xda\tu\xc9\x0f\xd3\xben9L\x1a\x06'

heroku = Heroku(app)

db = SQLAlchemy(app)

class Serializer(object):
    __public__ = None
    __exclude__ = None

    def serialize(self):
        data = {}
        for c in inspect(self).attrs.keys():
            if self.__public__ and c not in self.__public__: continue
            if self.__exclude__ and c in self.__exclude__: continue
            value = getattr(self, c)
            if isinstance(value, datetime.datetime):
              data[c] = value.strftime('%Y-%m-%d %H:%M:%S')  
            else:    
              data[c] = value
        return data 

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Client(db.Model, Serializer):
    __tablename__ = "clients"
    __public__ = ('id', 'name')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    requests = db.relationship('FeatureRequest', backref='client', lazy='dynamic')

    def __init__(self, name):
      self.name = name

    def __repr__(self):
      return '<Client %s>' % self.name


class ProductArea(db.Model, Serializer):
    __tablename__ = "product_areas"
    __public__ = ('id', 'area')
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(120), unique=True)
    requests = db.relationship('FeatureRequest', backref='product_area', lazy='dynamic')

    def __init__(self, area):
      self.area = area

    def __repr__(self):
      return '<ProductArea %s>' % self.area

class FeatureRequest(db.Model, Serializer):
    __tablename__ = "feature_requests"
    __public__ = ('id', 'title', 'description', 'client_id', 'priority',
                  'target_date', 'product_area_id')
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    priority = db.Column(db.Integer)
    target_date = db.Column(db.DateTime)
    product_area_id = db.Column(db.Integer, db.ForeignKey('product_areas.id'))
    __table_args__ = (UniqueConstraint('client_id', 'priority', name='_client_priority_ix'),)


    def __init__(self, title, description, client_id, priority, target_date, product_area_id):
      self.title = title
      self.description = description
      self.client_id = client_id
      self.priority = priority
      self.target_date = target_date
      self.product_area_id = product_area_id

    def __repr__(self):
      return '<FeatureRequest %s, %s>' % (self.title, self.client)

    
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)
 
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/v1.0/clients', methods = ['GET'])
def get_clients():
  clients = Client.query.all()  
  return json.dumps(Client.serialize_list(clients))

@app.route('/api/v1.0/clients', methods = ['POST'])
def add_client():
  data = request.get_json(force=True)
  db.session.add(Client(data['name']))
  db.session.commit()
  return jsonify({ 'msg': 'Client "%s" added' % data['name']});
  

@app.route('/api/v1.0/clients/<int:id>', methods = ['DELETE'])
def delete_client(id):
    try:
        client = Client.query.get(id)
        oldname = client.name
        db.session.delete(client)
        db.session.commit()
        return jsonify({ 'msg': 'Client "%s" deleted' % oldname});
    except:
      return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/api/v1.0/product_areas', methods = ['GET'])
def get_product_areas():
  areas = ProductArea.query.all()  
  return json.dumps(ProductArea.serialize_list(areas))

@app.route('/api/v1.0/product_areas', methods = ['POST'])
def add_product_area():
  data = request.get_json(force=True)
  db.session.add(ProductArea(data['area']))
  db.session.commit()
  return jsonify({ 'msg': 'Product Area "%s" added' % data['area']});

@app.route('/api/v1.0/product_areas/<int:id>', methods = ['DELETE'])
def delete_product_area(id):
    try:
        pa = ProductArea.query.get(id)
        oldname = pa.area
        db.session.delete(pa)
        db.session.commit()
        return jsonify({ 'msg': 'Product Area  "%s" deleted' % oldname});
    except:
      return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/api/v1.0/feature_requests', methods = ['GET', 'POST'])
def get_feature_requests():
  if request.method == 'POST':
      # TODO interpret json and create FeatureRequest record
      data = request.get_json(force=True)
      # reorder prioriy for specific client, if needed
      if db.session.query(FeatureRequest).filter_by(client_id=data['client_id'], priority=data['priority']).count():
        for fr in db.session.query(FeatureRequest).filter_by(client_id=data['client_id']).filter(
                                   FeatureRequest.priority>=data['priority']
                                  ).order_by(FeatureRequest.priority.desc()):
          fr.priority = fr.priority + 1
      freq = FeatureRequest(
               data['title'], data['description'],
               data['client_id'],
               data['priority'],
               datetime.datetime.strptime(data['target_date'], '%Y-%m-%d %H:%M:%S'),
               data['product_area_id'])
      db.session.add(freq)
      db.session.commit()

  freqs = FeatureRequest.query.limit(50).all()  
  return json.dumps(FeatureRequest.serialize_list(freqs))

@app.route('/api/v1.0/feature_requests/<int:id>', methods = ['GET'])
def get_feature_request(id):
    try:
        fr = FeatureRequest.query.get(id)
        return json.dumps(fr.serialize())
    except:
      return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/api/v1.0/feature_requests/<int:id>', methods = ['PUT'])
def update_feature_request(id):
      data = request.get_json(force=True)
      # reorder prioriy for specific client, if needed
      if 'priority' in data and db.session.query(FeatureRequest).filter(FeatureRequest.id != id).filter_by(
                          client_id=data['client_id'], priority=data['priority']).count():
        for fr in db.session.query(FeatureRequest).filter(FeatureRequest.id != id).filter_by(
                                   client_id=data['client_id']).filter(FeatureRequest.priority>=data['priority']
                                  ).order_by(FeatureRequest.priority.desc()):
          fr.priority = fr.priority + 1

      fr = FeatureRequest.query.get(id)
      fr.title = data.get('title', fr.title) 
      fr.description = data.get('description', fr.description) 
      fr.client_id = data.get('client_id', fr.client_id) 
      fr.priority = data.get('priority', fr.priority) 
      if 'target_date' in data:
        fr.target_date = datetime.datetime.strptime(data['target_date'], '%Y-%m-%d %H:%M:%S')
      fr.product_area_id = data.get('product_area_id', fr.product_area_id) 

      db.session.commit()
      return json.dumps(fr.serialize())

@app.route('/api/v1.0/feature_requests/<int:id>', methods = ['DELETE'])
def delete_feature_request(id):
    try:
        fr = FeatureRequest.query.get(id)
        oldname = fr.title
        db.session.delete(fr)
        db.session.commit()
        return jsonify({ 'msg': 'Feature Request  "%s" deleted' % oldname});
    except:
      return make_response(jsonify( { 'error': 'Not found' } ), 404)

if __name__ == '__main__':
  app.debug = True
  app.run() 
