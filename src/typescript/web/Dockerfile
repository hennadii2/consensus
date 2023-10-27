# #######################
# Install dependencies
# #######################
FROM node:17.6-alpine as base
WORKDIR /fe-app

ENV NEXT_TELEMETRY_DISABLED 1

RUN apk add --no-cache libc6-compat

COPY src/typescript/web/. ./
COPY src/typescript/web/.env.local ./.env.local
COPY src/typescript/web/.env ./.env

RUN yarn install --frozen-lockfile

# #######################
# Production image
# #######################
FROM base as prod
WORKDIR /fe-app

RUN yarn build

# #######################
# Production image
# #######################
FROM nginx:alpine
WORKDIR /fe-app

RUN apk add nodejs-current npm supervisor

# Copy nginx config files
RUN rm /etc/nginx/conf.d/*
RUN mkdir -p /var/log/supervisor && mkdir -p /etc/supervisor/conf.d
COPY src/typescript/web/nginx/default.conf /etc/nginx/conf.d/
COPY src/typescript/web/nginx/supervisor.conf /etc/supervisor.conf

# Copy nextjs build files
COPY --from=prod /fe-app/next.config.js ./next.config.js
COPY --from=prod /fe-app/package.json ./package.json
COPY --from=prod /fe-app/build ./build
COPY --from=prod /fe-app/node_modules ./node_modules
COPY --from=base /fe-app/public ./public
COPY --from=base /fe-app/.env.local ./.env.local
COPY --from=base /fe-app/.env ./.env

CMD ["supervisord", "-c", "/etc/supervisor.conf"]
