import os
import unittest
import tempfile
import json
from app import app, db 
from app import Client, ProductArea, FeatureRequest
import pdb 

# pdb.set_trace()

class TestFeatureRequests(unittest.TestCase):
  def setUp(self):
    app.config.from_pyfile('settings.cfg')
    db.session.close()
    db.drop_all()
    db.create_all()
    # populate some data
    db.session.add(Client('Client A'))
    db.session.add(Client('Client B'))
    db.session.add(Client('Client C'))

    db.session.add(ProductArea('Policies'))
    db.session.add(ProductArea('Billing'))
    db.session.add(ProductArea('Claim'))
    db.session.add(ProductArea('Reports'))

    db.session.commit()
    self.appc = app.test_client()
    #pdb.set_trace()


  def test_clients(self):
    client = Client('Marina')
    db.session.add(client)
    db.session.commit()
    clients = Client.query.all()
    assert client in clients

  def test_noreqs(self):
    rv = self.appc.get('/')
    assert b'No feature requests so far' in rv.data

  def test_api_clients(self):
    rv = self.appc.get('/api/v1.0/clients')  
    ca = json.loads(rv.data)
    assert len(ca)== 3
    rv = self.appc.post('/api/v1.0/clients', 
                        data=json.dumps(dict(name='Murzik')),
                        content_type='application/json')
    assert b'Murzik' in rv.data
    assert b'added' in rv.data
    assert Client.query.count() == 4
    c = Client.query.filter_by(name='Murzik').first()
    rv = self.appc.delete('/api/v1.0/clients/%d' % c.id)
    assert b'deleted' in rv.data
    assert Client.query.count() == 3

  def test_api_product_areas(self):
    rv = self.appc.get('/api/v1.0/product_areas')  
    pa = json.loads(rv.data)
    assert len(pa)== 4
    rv = self.appc.post('/api/v1.0/product_areas', 
                        data=json.dumps(dict(area='QA')),
                        content_type='application/json')
    assert b'QA' in rv.data
    assert b'added' in rv.data
    assert ProductArea.query.count() == 5
    c = ProductArea.query.filter_by(area='QA').first()
    rv = self.appc.delete('/api/v1.0/product_areas/%d' % c.id)
    assert b'deleted' in rv.data
    assert ProductArea.query.count() == 4

  def test_api_feature_requests(self):
    rv = self.appc.get('/api/v1.0/feature_requests')  
    j = json.loads(rv.data)
    assert len(j) == 0
    rv = self.appc.post('/api/v1.0/feature_requests', 
        data=json.dumps(dict(
            title='Feature 1',
            description='La-la-la',
            target_date='2017-09-02 00:00:00',
            client_id=1,
            priority=1,
            product_area_id=1)), content_type='application/json')
    assert b'Feature 1' in rv.data

    rv = self.appc.post('/api/v1.0/feature_requests', 
        data=json.dumps(dict(
            title='Feature 2',
            description='Bip-bip-bip',
            target_date='2017-09-04 00:00:00',
            client_id=1,
            priority=1,
            product_area_id=1)), content_type='application/json')

    rv = self.appc.post('/api/v1.0/feature_requests', 
        data=json.dumps(dict(
            title='Feature 3',
            description='Blues',
            target_date='2017-09-04 00:00:00',
            client_id=1,
            priority=1,
            product_area_id=1)), content_type='application/json')

    assert FeatureRequest.query.count() == 3
    # check that priority for the same client is not duplicated
    assert FeatureRequest.query.filter_by(client_id=1, priority=1).count() == 1
    assert FeatureRequest.query.count() == 3
    fr = FeatureRequest.query.filter_by(client_id=1, priority=2).first()
    rv = self.appc.put('/api/v1.0/feature_requests/%d' % fr.id, 
        data=json.dumps(dict(
            target_date='2017-09-15 00:00:00',
            priority=3,
            product_area_id=1)), content_type='application/json')
    assert FeatureRequest.query.filter_by(client_id=1, priority=4).count() == 1

    rv = self.appc.delete('/api/v1.0/feature_requests/%d' % fr.id) 
    assert b'deleted' in rv.data
    assert fr.title in rv.data
    assert FeatureRequest.query.count() == 2


if __name__ == '__main__':
    print 'Hi'
    unittest.main()    
