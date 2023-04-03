# Image Service

[![CI pipeline](https://github.com/holdupleftandtheapressstart/reshape/actions/workflows/ci.yaml/badge.svg)](https://github.com/holdupleftandtheapressstart/reshape/actions/workflows/ci.yaml)

REST API for image management.

| Path | Method | Description |
|---|---|---|
| `/api/v1/images/upload` | `POST` | Upload binary images using `multipart/form-data` |
| `/api/v1/images/` | `POST` | Create image using `url` |
| `/api/v1/images/{image_id}` | `GET` | Get image metadata |
| `/api/v1/images/{image_id}` | `PUT` | Update image (crop) |
| `/api/v1/images/{source_image_id}/diff/{target_image_id}` | `GET` | Get image differences using `phash` |

## Design decisions

* `FastAPI` as a web framework (async, type hints, swagger)
* Store images on disk, metadata (name, location, hash) in `sqlite`. Simplest option given the scope of the project.
* Use [phash](https://www.phash.org/) for image comparison. I used it before and it works well.

## Prerequisites

Install `poetry`

```bash
$ curl -sSL https://install.python-poetry.org | python3 -
```

Install dependencies

```bash
$ poetry update
```

Install `pre-commit`:

```bash
$ pip install --user virtualenv
$ pip install --user pre-commit
$ pre-commit install
```

Prepare environment variables

```bash
$ cp .env.example .env
$ vi .env
```

Load variables in your shell:

```bash
$  set -o allexport; source .env; set +o allexport
```

Or use `dotenv`.

## Run

### Run locally

Start server

```bash
poetry run uvicorn app.main:app
```

### Run container

Build container

```
$ docker build -t app .
```

Run container

```
$ docker run --rm --env-file .env -p 8000:8000 app
```

### API documentation

Open documentation

```
$ xdg-open http://localhost:8000/redoc
```

## Test

```bash
$ poetry run pytest
```

## TODOs

* Clean up exceptions and add custom error handler
* Persistence layer should be block storage (S3, GCS, etc)
* Metadata should be stored in a "proper" database (Postgres, MySQL, etc)
* Some queue for async tasks (cropping, image processing)
* Unify a bit more image creation `url` vs `upload`
* Cleanup image format handling
* Add more tests
* Add more documentation
* Add more logging
