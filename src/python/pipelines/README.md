# src/python/pipelines
Beam pipelines for data transformation, DB ingestion, search indexing, etc.

### Connecting to a DB with DirectRunner
In order for the DirectRunner to connect to our DB, you need to use the [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy).

Review those docs for details, but here's a summary of the steps for quick reference:

0. Download and install the `cloud-sql-proxy` binary (see the [docs](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install) for your specific platform)
1. Start the proxy in a separate terminal: `./cloud-sql-proxy consensus-334718:us-central1:<db_name> -c <secret_file_path>`
2. (Optional) Test the connection: `psql "host=127.0.0.1 port=5432 sslmode=disable dbname=postgres user=postgres"`
3. Pass the `--db_host_override="host.docker.internal"` and `--db_port_override=5432` to the `MainDbEnv` constructor

Step should work as-is for Mac/Windows, but there is one extra step needed for Linux: see [this SO thread](https://stackoverflow.com/questions/24319662/from-inside-of-a-docker-container-how-do-i-connect-to-the-localhost-of-the-mach).