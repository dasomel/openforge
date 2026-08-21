# OpenForge reusable Dockerfile baseline
# Pin the base image by digest before production use.
ARG BASE_IMAGE=debian:bookworm-slim
FROM ${BASE_IMAGE} AS runtime

ARG APP_USER=app
ARG APP_UID=10001

RUN groupadd --gid ${APP_UID} ${APP_USER} \
 && useradd --uid ${APP_UID} --gid ${APP_UID} --create-home --shell /usr/sbin/nologin ${APP_USER}

WORKDIR /app
COPY --chown=${APP_UID}:${APP_UID} . /app

USER ${APP_USER}

# Replace with the application-specific command and health endpoint.
EXPOSE 8080
ENTRYPOINT ["/app/bin/app"]
