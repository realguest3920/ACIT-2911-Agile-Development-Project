import pytest
import pymongo
import mongomock
from Flask_API import create_app
from Flask_API.marketplace import routes

@pytest.fixture
def flask_app(tmp_path):
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture
def test_Data() :
    return {
        "title": "Test2",
        "creator": "junugim4",
        "price": 99.99,
        "condition": "Very Good",
        "description": "I deleted this description"
    }

@pytest.fixture
def mock_DB(monkeypatch) :
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

def test_status(client) :
    response = client.get("/marketplace/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok"}

def test_get_all_listings(client, mock_DB) :

    resp = client.get("/marketplace/listings")

    assert resp.status_code == 200

    data = resp.get_json()
    assert len(data) == 2
    titles = {title["title"] for title in data}
    creators = {creator["creator"] for creator in data}
    prices = {price["price"] for price in data}
    conditions = {condition["condition"] for condition in data}
    descriptions = {description["description"] for description in data}

    assert titles == {"Test1", "Test2"}
    assert creators == {"realguest3920", "junugim4"}
    assert prices == {99.99, 29.99}
    assert conditions == {"Very Good", "Good"}
    assert descriptions == {"I hate this description", "descriptiond"}

def test_get_listing(client, mock_DB) :

    resp = client.get("/marketplace/listings/0")

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Test1"
    assert data["creator"] == "realguest3920"
    assert data["price"] == 99.99
    assert data["condition"] == "Very Good"
    assert data["description"] == "I hate this description"

def test_get_listing_does_not_exist(client, mock_DB) :

    resp = client.get("/marketplace/listings/9999")

    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data
    assert data["error"] == "listing does not exist"

def test_post_normal_listing(client, mock_DB, test_Data) :
    resp = client.post(
        "/marketplace/listings/create",
        json=test_Data,
    )

    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == test_Data["title"]
    assert data["creator"] == test_Data["creator"]
    assert data["price"] == test_Data["price"]
    assert data["condition"] == test_Data["condition"]
    assert data["description"] == test_Data["description"]

def test_post_listing_no_params(client, mock_DB, test_Data) :
    resp = client.post("/marketplace/listings/create", json={})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_post_listing_invalid_params(client, mock_DB, test_Data) :
    resp = client.post("/marketplace/listings/create", json={"title": test_Data["title"]})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_update_listing_one_value(client, mock_DB, test_Data) :
    testTitle = "I updated this!"

    resp = client.put("/marketplace/listings/update/0", json={"title" : testTitle})

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == testTitle

def test_update_listing_multiple_values(client, mock_DB, test_Data) :
    testTitle = "I changed it again!!"
    testPrice = 69.29
    testCondition = "Very Good"

    resp = client.put("/marketplace/listings/update/0", json={
        "title" : testTitle,
        "condition" : testCondition,
        "price" : testPrice
    })

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == testTitle
    assert data["price"] == testPrice
    assert data["condition"] == testCondition

def test_update_listing_no_params(client, mock_DB, test_Data) :
    resp = client.put("/marketplace/listings/update/0", json={})

    assert resp.status_code == 200

def test_update_listing_invalid_params(client, mock_DB, test_Data) :
    testTitle = "I need an error!"

    resp = client.put("/marketplace/listings/update/0", json={"deleted" : testTitle})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_delete_listing(client, mock_DB) :
    resp = client.delete("/marketplace/listings/delete/0")
    assert resp.status_code == 200

    resp = client.get("/marketplace/listings")

    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    titles = {title["title"] for title in data}
    creators = {creator["creator"] for creator in data}
    prices = {price["price"] for price in data}
    conditions = {condition["condition"] for condition in data}
    descriptions = {description["description"] for description in data}
    assert titles == {"Test2"}
    assert creators == {"junugim4"}
    assert prices == {29.99}
    assert conditions == {"Good"}
    assert descriptions == {"descriptiond"}

def test_delete_listing_does_not_exist(client, mock_DB) :
    resp = client.delete("/marketplace/listings/delete/999")
    
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data