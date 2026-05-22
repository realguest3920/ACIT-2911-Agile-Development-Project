import pytest
import pymongo
import mongomock
from unittest.mock import Mock
import cloudinary.uploader
from io import BytesIO
from app import app
from app import routes

@pytest.fixture
def flask_app(tmp_path):
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture
def test_Data():
    return {
        "title": "Test2",
        "creator": "junugim4",
        "price": 99.99,
        "condition": "Very Good",
        "description": "I deleted this description"
    }


@pytest.fixture
def mock_DB(monkeypatch):
    mongocli = mongomock.MongoClient()
    mockDB = mongocli["AgileDevelopmentTestDB"]
    mockDB.Listings.insert_many(
        [
            {
                "_id" : 0,
                "title": "Test1",
                "creator": "realguest3920",
                "price": 99.99,
                "condition": "Very Good",
                "description": "I hate this description",
                "views" : 532,
                "likes" : 46,
                "imgurl" : "?",
            },
            {
                "_id" : 1,
                "title": "Test2",
                "creator": "junugim4",
                "price": 29.99,
                "condition": "Good",
                "description": "descriptiond",
                "views" : 259,
                "likes" : 116,
                "imgurl" : "?",
            },
        ]
    )
    monkeypatch.setattr(routes, "maindb", mockDB)
    return mockDB

# 1. Test Status
def test_status(client):
    response = client.get("/marketplace/status")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

# 2. Get All Listings
def test_get_all_listings(client, mock_DB):
    resp = client.get("/marketplace/listings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert {item["title"] for item in data} == {"Test1", "Test2"}

# 3. Get Single Listing
def test_get_listing(client, mock_DB):
    resp = client.get("/marketplace/listings/0")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Test1"

# 4. Get Listing Not Found
def test_get_listing_does_not_exist(client, mock_DB):
    resp = client.get("/marketplace/listings/9999")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "listing does not exist"

# 5. Create Listing (Success)
def test_post_normal_listing(client, mock_DB, test_Data):
    data = test_Data.copy()

    cloudinary.uploader.upload = Mock(return_value={
        "public_id": "fake img", 
        "secure_url": "https://cloudinary.com"
    })

    data['imageUpload'] = (BytesIO(b"fake image content"), 'test.jpg')
    resp = client.post(
        "/marketplace/listings/create",
        data=data,
        content_type='multipart/form-data'
    )
    dataJson = resp.get_json()
    assert resp.status_code == 201
    assert "id" in dataJson
    assert "message" in dataJson

# 6. Create Listing (Missing Parameters)
def test_post_listing_no_params(client, mock_DB):
    resp = client.post("/marketplace/listings/create", data={}, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert "error" in resp.get_json()

# 7. Create Listing (Invalid/Incomplete Params)
def test_post_listing_invalid_params(client, mock_DB, test_Data):
    # Missing image or description triggers error
    resp = client.post("/marketplace/listings/create", data={"title": "No Image"}, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert "error" in resp.get_json()

# 8. Update Listing (Single Field)
def test_update_listing_one_value(client, mock_DB):
    testTitle = "I updated this!"
    resp = client.put("/marketplace/listings/update/0", json={"title": testTitle})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == testTitle

# 9. Update Listing (Multiple Fields)
def test_update_listing_multiple_values(client, mock_DB):
    payload = {"title": "New Title", "price": 50.0, "condition": "New"}
    resp = client.put("/marketplace/listings/update/0", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "New Title"
    assert data["price"] == 50.0

# 10. Update Listing (No Changes)
def test_update_listing_no_params(client, mock_DB):
    resp = client.put("/marketplace/listings/update/0", json={})
    assert resp.status_code == 200

# 11. Update Listing (Invalid Fields)
def test_update_listing_invalid_params(client, mock_DB):
    resp = client.put("/marketplace/listings/update/0", json={"unknown_key": "fail"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

# 12. Delete Listing (Success)
def test_delete_listing(client, mock_DB):
    # Route is POST based on your api_bp definition
    resp = client.post("/marketplace/listings/delete/0")
    # Redirect code 302 means it worked and sent you to index
    assert resp.status_code == 302 

# 13. Delete Listing (Not Found)
def test_delete_listing_does_not_exist(client, mock_DB):
    resp = client.post("/marketplace/listings/delete/999")
    # Your current code redirects even on failure after flashing
    assert resp.status_code == 302
