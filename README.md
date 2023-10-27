# common

Consensus monorepo

### Required Dependencies

- Python 3.9
- Git Large File System (LFS)
  https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage
- Docker

### Common commands

Run `make help` to view a list of commonly run commands with aliases.

### To run the web app

1. Install required dependencies
1. Clone this repo and `cd` into it
1. Run `git lfs pull`
1. Setup `.env.local` files for frontend and backend, ask someone on the team for help with this
1. Run `make web` and wait for it to fully start. You will see a message that says: `Application startup complete.`
1. Keep `make web` running, and from another terminal run `make web-init` to populate mock backend data
1. Open `localhost:3000/search` in your browser

### Subscribe to Premium in your local environment

To manage subscriptions locally, you'll need to configure the Stripe CLI to forward requests to the Next.js webhook listener.

1. First, Run `make web-stripe-init` to populate locally running web app backend with stripe data.
1. Next, we'll need to Install and run the stripe local listener. Download and install [stripe CLI](https://stripe.com/docs/stripe-cli).
1. In the [stripe dashboard](https://dashboard.stripe.com/webhooks/create?endpoint_location=local), choose "test in a local environment". Follow the instructions to run the local listener:

   ```
   stripe login

   # Forward webhook requests to the nextjs api endpoint
   stripe listen --forward-to localhost:3000/api/stripe/webhook/
   ```

1. This will output a "webhook signing secret" in the terminal. We'll need to provide this to the Next.js runtime as an environment variable. In `common/src/typescript/web/.env.local`, add the secret:
   ```
   ...
   FE_STRIPE_WEBHOOK_SECRET=whsec_123 (from terminal)
   ```
1. In your local app running on localhost:3000, navigate to your subscriptions, and purchase a "test mode" Subscription using one of the [stripe test credit cards](https://stripe.com/docs/testing#cards). The stripe cli should output a success message showing that the subscription succeeded:
   ```
   ...
   2023-09-08 17:53:39   --> customer.subscription.created [evt_123]
   2023-09-08 17:53:39  <--  [200] POST http://localhost:3000/api/stripe/webhook/ [evt_123]
   ```
1. Confirm your subscription by refreshing the app. In the database, you'll also see a new row added to the customer_subscriptions table.

### Troubleshooting

If you encounter `ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+ [...]` when running the `./pants` script:

1. `echo 'urllib3<2' > constraints.txt`
1. `echo 'export PIP_CONSTRAINT=constraints.txt' > .pants.bootstrap`
1. `rm -rf ~/.cache/pants/setup`
   - Note: This removes the cached Pants installation; you may want to back up the folder first.

Then, the next time you run the `./pants` script, it will bootstrap the installation using the passed `urllib3` constraints.
