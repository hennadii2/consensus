ARG BUILD_ENV=no_models

FROM python:3.9 as base
WORKDIR /shared/common

# #######################
# Pre-cache models into Docker image
# #######################
FROM base as build_cache_models
ARG HF_ACCESS_TOKEN=
COPY src.python.web.scripts/install_web_chat_gpt_plugin_models.pex /bin/cache_models
RUN /bin/cache_models --hf_access_token=${HF_ACCESS_TOKEN}

# #######################
# Skip caching, models will be downloaded at runtime
# #######################
FROM base as build_no_models

# #######################
# Build
# #######################
FROM build_${BUILD_ENV}

# Copy public directory into the image
RUN mkdir -p web/chat_gpt_plugin/app
COPY src/python/web/chat_gpt_plugin/app/public web/chat_gpt_plugin/app/public/

# Copy binary into the image
COPY src.python.web.chat_gpt_plugin/chat_gpt_plugin.pex /bin/chat_gpt_plugin

EXPOSE 8080

CMD [ "/bin/chat_gpt_plugin" ]
