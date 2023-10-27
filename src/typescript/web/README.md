## Requirements

### Node version 16.5.0

If you are managing multiple projects with different nodejs versions. Please install [NVM](https://github.com/nvm-sh/nvm). After installing, run the commands below

```bash
$ nvm install 16.5.0
$ nvm use
```

### Yarn

```bash
$ npm install --global yarn
```

## Installation

```bash
$ yarn install
```

## Global variable

Rename .env.example to .env

## Running the development server

```bash
$ npm run dev
# or
$ yarn dev
```

## Running the component tests

```bash
$ npm run test --watchAll --verbose
# or
$ yarn test --watchAll --verbose
```

## Opening cypress UI with option to run the integration tests

```bash
$ npm run cypress:open
# or
$ yarn cypress:open
```

## Running the integration tests using terminal

```bash
$ npm run cypress:spec
# or
$ yarn cypress:spec
```

## Building the project

```bash
$ npm run build
# or
$ yarn build
```
