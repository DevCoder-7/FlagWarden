FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system flagwarden && useradd --system --gid flagwarden flagwarden
COPY pyproject.toml README.md ./
COPY flagwarden ./flagwarden
COPY challenge_packs ./challenge_packs
COPY miniapp ./miniapp
COPY alembic.ini ./
COPY alembic ./alembic
RUN pip install --no-cache-dir ".[postgres]"
USER flagwarden
EXPOSE 8000
CMD ["uvicorn", "flagwarden.main:app", "--host", "0.0.0.0", "--port", "8000"]
