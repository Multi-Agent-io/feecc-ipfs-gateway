# Feecc IPFS Gateway

## Overview

Feecc IPFS Gateway is a microservice, designed to publish files to IPFS and Pinata cloud. It also lets you publish file
CIDs to Robonomics network datalog.

It provides a simple REST API interface to publish files either by their paths on the host or by providing them in a
request body as multipart form data. It also handles user authentication.

Feecc IPFS Gateway comes as a part of the Feecc QA system - a Web3 enabled quality control system.

IPFS Gateway is a microservice that is written in asynchronous Python using FastAPI framework and httpx library.

## Deployment

The app is supposed to be run in a Docker container and can be configured by setting several environment variables.

> Note, that we assume a Linux host in this guide, however you can also run IPFS Gateway on any other OS,
> but be warned: timezone is defined by mounting host `/etc/timezone` and `/etc/localtime` files inside the container,
> which are not present on Windows machines, so you might end up with UTC time inside your container.

Start by cloning the git repository onto your
machine: `git clone https://github.com/Multi-Agent-io/feecc-ipfs-gateway.git`

Enter the app directory and modify the `docker-compose.yml` file to your needs by changing the environment variables
(discussed in the configuration part).

```
cd feecc-ipfs-gateway
vim docker-compose.yml
```

When you are done configuring your installation, build and start the container using docker-compose:
`sudo docker-compose up --build`

Verify your deployment by going to http://127.0.0.1:8082/docs in your browser. You should see the SwaggerUI API
specification page. Continue from there.

## Configuration

To configure your IPFS Gateway deployment edit the environment variables, provided in `docker-compose.yml` file.

### Environment variables

- `MONGODB_URI` - Your MongoDB connection URI ending with `/db-name`.
- `PRODUCTION_ENVIRONMENT` - Leave null if you want testing credentials to work, otherwise set it to `true`.
- `LOCAL_IPFS_ENABLED`- Whether to enable local IPFS node publishing or not. Defaults to `false`.
- `PINATA_ENABLED`- Whether to upload files to Pinata.cloud or not. Defaults to `false`.
- `PINATA_API`- Pinata.cloud credentials. Leave empty if you don't need it.
- `PINATA_SECRET_API` - Pinata.cloud credentials. Leave empty if you don't need it.
- `ROBONOMICS_ENABLE_DATALOG`- Whether to post CIDs to Robonomics network datalog or not. Defaults to `false`.
- `ROBONOMICS_SUBSTRATE_NODE_URL` - Robonomics node URL in case you want to use a non-default node.
- `ROBONOMICS_ACCOUNT_SEED`- Robonomics network account seed. Leave empty if you don't need it.
- `AUTH_MODE`- Authentication mode. Available options are "analytics" (auth by analytics login), "workbench" (auth by card id) and "noauth" (auth w/o credentials).