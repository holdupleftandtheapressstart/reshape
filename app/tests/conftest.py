from typing import Generator, Callable

import os
import pytest
import random
import string

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.core.config import settings


@pytest.fixture(name="temp_image_path", scope="module")
def fixture_temp_image_path(tmp_path_factory: Generator) -> str:
    settings.IMAGE_UPLOAD_DIR = tmp_path_factory.mktemp("images")  # type: ignore
    return settings.IMAGE_UPLOAD_DIR


@pytest.fixture(name="test_image_path", scope="module")
def fixture_test_image_path() -> str:
    return os.path.dirname(__file__) + "/images"


@pytest.fixture(scope="session")
def google_logo_url() -> str:
    return "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"


@pytest.fixture(scope="session")
def wikipedia_logo_url() -> str:
    return "https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png"


@pytest.fixture(scope="session")
def gif_url() -> str:
    return "https://upload.wikimedia.org/wikipedia/commons/1/14/Cerebellum_animation_small.gif"


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client(temp_image_path: Generator) -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(name="random_lower_string")
def fixture_random_lower_string() -> Callable[[], str]:
    return lambda: "".join(random.choices(string.ascii_lowercase, k=32))


@pytest.fixture(name="valid_url_image", scope="function")
def fixture_valid_url_image(
    random_lower_string: Callable[[], str],
    google_logo_url: str,
) -> Callable[[], dict]:
    return lambda: {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "url": google_logo_url,
        "image": "plm",
    }


@pytest.fixture(name="created_url_image", scope="function")
def fixture_url_created_image(
    client: TestClient, valid_url_image: Callable[[], dict]
) -> dict:
    response = client.post(
        "/api/v1/images",
        json=valid_url_image(),
    )

    assert response.status_code == 200
    return response.json()
