# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye
WORKDIR /app
COPY --from=pythonbuilder /builder/.venv .venv
COPY . .
RUN .venv/bin/python -m pip install -r requirements.txt
CMD ["/app/.venv/bin/python", "can_demo.py"]