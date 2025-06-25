# GoSex services deployment

## Clone

```shell
git clone https://github.com/rosgossex/gosex-deploy.git
git submodule update --init --recursive --remote
```

## Run

```shell
docker compose --env-file .env up -d --wait --build
```