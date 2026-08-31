FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --gid 65532 launchrail && useradd --uid 65532 --gid launchrail --no-create-home launchrail
COPY --from=builder /wheels /wheels
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels
COPY platform_api ./platform_api
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["python", "-m", "platform_api.run"]
