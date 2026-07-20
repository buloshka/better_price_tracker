# syntax=docker/dockerfile:1

FROM dhi.io/python:3.14-dev AS builder

WORKDIR /app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

FROM dhi.io/python:3.14

WORKDIR /app

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
