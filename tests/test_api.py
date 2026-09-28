def login(client):
    client.post('/api/register',json={'username':'tester','email':'tester@example.com','password':'password123'})
    return client.post('/api/login',json={'email':'tester@example.com','password':'password123'})

def test_health(client):
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_auth(client):
    r=login(client); assert r.status_code==200
    s=client.get('/api/session-info'); assert s.status_code==200 and s.json()['username']=='tester'

def test_home_fallback(client):
    login(client)
    r=client.post('/api/generate-home',json={'budget':30000,'rooms':[{'room_type':'Living Room','quantity':1}],'style':'modern','notes':''})
    assert r.status_code==200 and r.json()['planner']=='home' and r.json()['items']

def test_party_fallback(client):
    login(client)
    r=client.post('/api/generate-party',json={'budget':50000,'guest_count':40,'event_type':'birthday','venue_type':'indoor','city':'Coimbatore','notes':''})
    assert r.status_code==200 and r.json()['planner']=='party'

def test_history(client):
    login(client)
    client.post('/api/generate-home',json={'budget':10000,'rooms':[{'room_type':'Bedroom','quantity':1}],'style':'simple','notes':''})
    r=client.get('/api/history'); assert r.status_code==200 and len(r.json())==1
