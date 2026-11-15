import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from app import main

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DB', str(tmp_path / 'test.db'))
    main.init_db()
    return TestClient(main.app)

def test_create_list_delete(client):
    payload={'track':'A1','start_min':480,'end_min':540,'train':'FREIGHT 101'}
    response=client.post('/api/slots',json=payload)
    assert response.status_code==201
    slot_id=response.json()['id']
    assert len(client.get('/api/slots').json())==1
    assert client.delete(f'/api/slots/{slot_id}').status_code==204
    assert client.get('/api/slots').json()==[]

def test_overlap_rejected_and_adjacent_allowed(client):
    base={'track':'A1','start_min':100,'end_min':200,'train':'T1'}
    assert client.post('/api/slots',json=base).status_code==201
    assert client.post('/api/slots',json={**base,'start_min':150,'end_min':250,'train':'T2'}).status_code==409
    assert client.post('/api/slots',json={**base,'start_min':200,'end_min':300,'train':'T3'}).status_code==201
    assert client.post('/api/slots',json={**base,'track':'B1','train':'T4'}).status_code==201

def test_invalid_input(client):
    base={'track':'A1','start_min':200,'end_min':100,'train':'T1'}
    assert client.post('/api/slots',json=base).status_code==422
    assert client.post('/api/slots',json={**base,'track':'../../bad'}).status_code==422
    assert client.delete('/api/slots/999').status_code==404

def test_home(client):
    assert 'YardFlow' in client.get('/').text
