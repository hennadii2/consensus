ARG BUILD_ENV=no_models

FROM python:3.9 as base
WORKDIR /shared/common

# #######################
# Pre-cache models into Docker image
# #######################
FROM base as build_cache_models
ARG HF_ACCESS_TOKEN=
COPY src.python.web.scripts/install_web_backend_models.pex /bin/cache_models
RUN /bin/cache_models --hf_access_token=${HF_ACCESS_TOKEN}

# #######################
# Skip caching, models will be downloaded at runtime
# #######################
FROM base as build_no_models

# #######################
# Build
# #######################
FROM build_${BUILD_ENV}

COPY src.python.web.backend/backend.pex /bin/backend

EXPOSE 8080

CMD [ "/bin/backend" ]
