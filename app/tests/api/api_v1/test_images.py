from PIL import Image
from typing import Callable
import numpy as np

import pytest

from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_image_correct_url(
    client: TestClient, valid_url_image: Callable[[], dict]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/images",
        json=valid_url_image(),
    )
    assert response.status_code == 200


def test_create_image_correct_binary(client: TestClient, test_image_path: str) -> None:
    with open(f"{test_image_path}/image0.jpeg", "rb") as file:
        response = client.post(
            f"{settings.API_V1_STR}/images/upload",
            data={
                "name": "test",
                "description": "test",
            },
            files={"file": file},
        )
    assert response.status_code == 200


def test_create_image_url_unsupported_image_format(
    client: TestClient, gif_url: str
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/images",
        json={
            "name": "test",
            "description": "test",
            "url": gif_url,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Image format not supported"}


def test_create_image_binary_unsupported_image_format(
    client: TestClient, test_image_path: str
) -> None:
    with open(f"{test_image_path}/cerebellum.gif", "rb") as file:
        response = client.post(
            f"{settings.API_V1_STR}/images/upload",
            data={
                "name": "test",
                "description": "test",
            },
            files={"file": file},
        )
    assert response.status_code == 400
    assert response.json() == {"detail": "Image format not supported"}


def test_create_image_incorrect_url(
    client: TestClient, valid_url_image: Callable[[], dict]
) -> None:
    payload = valid_url_image()
    payload["url"] = "incorrect"

    response = client.post(
        f"{settings.API_V1_STR}/images/",
        json=payload,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "invalid or missing URL scheme",
                "type": "value_error.url.scheme",
            }
        ],
    }


def test_create_image_unavailable_url(
    client: TestClient, valid_url_image: Callable[[], dict]
) -> None:
    payload = valid_url_image()
    payload["url"] = "http://unavailable.url"

    response = client.post(
        f"{settings.API_V1_STR}/images/",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Error while downloading image"}


def test_get_image(client: TestClient, created_url_image: dict) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/images/{created_url_image['id']}",
    )

    assert response.status_code == 200
    assert response.json() == created_url_image


def test_get_image_not_found(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/images/00000000-0000-0000-0000-000000000000",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}


def test_diff_equal_images(
    client: TestClient, valid_url_image: Callable[[], dict]
) -> None:
    response_source = client.post(
        f"{settings.API_V1_STR}/images",
        json=valid_url_image(),
    )
    assert response_source.status_code == 200

    response_target = client.post(
        f"{settings.API_V1_STR}/images",
        json=valid_url_image(),
    )
    assert response_target.status_code == 200
    assert response_source.json()["id"] != response_target.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/images/{response_source.json()['id']}/diff/{response_target.json()['id']}"
    )
    assert response.json() == {
        "source_image_id": response_source.json()["id"],
        "target_image_id": response_target.json()["id"],
        "diff": 0.0,
    }


def test_diff_non_equal_images(
    client: TestClient, valid_url_image: Callable[[], dict], wikipedia_logo_url: str
) -> None:
    response_source = client.post(
        f"{settings.API_V1_STR}/images",
        json=valid_url_image(),
    )
    assert response_source.status_code == 200

    payload = valid_url_image()
    payload["url"] = wikipedia_logo_url
    response_target = client.post(
        f"{settings.API_V1_STR}/images",
        json=payload,
    )
    assert response_target.status_code == 200
    assert response_source.json()["id"] != response_target.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/images/{response_source.json()['id']}/diff/{response_target.json()['id']}"
    )
    assert response.json()["diff"] == pytest.approx(36.0, 0.0001)


def test_diff_url_vs_upload(
    client: TestClient,
    valid_url_image: Callable[[], dict],
    test_image_path: str,
    wikipedia_logo_url: str,
) -> None:
    payload = valid_url_image()
    payload["url"] = wikipedia_logo_url
    response_source = client.post(
        f"{settings.API_V1_STR}/images",
        json=payload,
    )
    assert response_source.status_code == 200

    with open(f"{test_image_path}/wikipedia_logo.png", "rb") as file:
        response_target = client.post(
            f"{settings.API_V1_STR}/images/upload",
            data={
                "name": "test",
                "description": "test",
            },
            files={"file": file},
        )
    assert response_target.status_code == 200
    assert response_source.json()["id"] != response_target.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/images/{response_source.json()['id']}/diff/{response_target.json()['id']}"
    )
    assert response.json()["diff"] == pytest.approx(0, 0.0001)


def test_center_crop(
    client: TestClient,
    valid_url_image: Callable[[], dict],
    wikipedia_logo_url: str,
    temp_image_path: str,
    test_image_path: str,
) -> None:
    with open(f"{test_image_path}/black_white.png", "rb") as file:
        response = client.post(
            f"{settings.API_V1_STR}/images/upload",
            data={
                "name": "test",
                "description": "test",
            },
            files={"file": file},
        )
    assert response.status_code == 200

    img = Image.open(f"{temp_image_path}/{response.json()['id']}")
    data = np.asarray(img, dtype="int32")
    assert data.sum() != 0

    image_id = response.json()["id"]
    pil_image = Image.open(f"{temp_image_path}/{image_id}")
    assert pil_image.size != (100, 100)

    # update image and check if it has the right size and is completely white
    response = client.put(
        f"{settings.API_V1_STR}/images/{image_id}?width=100&height=100"
    )
    assert response.status_code == 204

    pil_image = Image.open(f"{temp_image_path}/{image_id}")
    assert pil_image.size == (100, 100)

    data = np.asarray(pil_image, dtype="int32")
    data.sum()
    assert data.sum() == 0


def test_center_crop_invalid(
    client: TestClient,
    valid_url_image: Callable[[], dict],
    wikipedia_logo_url: str,
    temp_image_path: str,
    test_image_path: str,
) -> None:
    with open(f"{test_image_path}/black_white.png", "rb") as file:
        response = client.post(
            f"{settings.API_V1_STR}/images/upload",
            data={
                "name": "test",
                "description": "test",
            },
            files={"file": file},
        )
    assert response.status_code == 200

    image_id = response.json()["id"]
    # negative crop
    response = client.put(
        f"{settings.API_V1_STR}/images/{image_id}?width=-1000&height=-1000"
    )
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Error while cropping image Coordinate 'right' is less than 'left'"
    }
