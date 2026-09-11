FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/

WORKDIR /droptop_bot

COPY pyproject.toml uv.lock ./

RUN apk update && apk add \
    jpeg-dev \
    zlib-dev \
    libpng-dev \
    && rm -rf /var/cache/apk/*

RUN uv sync --locked --no-install-project

COPY . .

CMD ["uv", "run", "--no-sync", "python", "main.py"]