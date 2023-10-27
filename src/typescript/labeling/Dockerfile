# #######################
# Install dependencies
# #######################
FROM node:17.6-alpine as base
WORKDIR /fe-app

ENV NEXT_TELEMETRY_DISABLED 1

RUN apk add --no-cache libc6-compat

COPY src/typescript/labeling ./
COPY src/typescript/labeling/.env.local ./.env.local
COPY src/typescript/labeling/.env ./.env

RUN yarn install --frozen-lockfile

# #######################
# Production image
# #######################
FROM base as prod
WORKDIR /fe-app

RUN yarn build

EXPOSE 8080

CMD ["yarn", "start", "--", "-p", "8080"]
