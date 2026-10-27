# potyk-io

> personal internet

## Links

- [Github](https://github.com/potykion/potyk-io.git)

## Запуск на локалке

```sh
python -m flask run --debug 
```

## Prod 

- ВМ (Yandex Cloud): 2 vCPU (100%), 2 ГБ RAM, 20 ГБ диск, Intel Ice Lake.  
- Gunicorn: `workers=2` / `threads=4` / `gthread` — под 2 ядра и SQLite (см. `ops/gunicorn.conf.py`).
- Инфра в репо: `ops/` (systemd, Caddyfile, gunicorn, `ops/cloudflare/`).

## Operations 


### First time deploy to prod 

```shell
ssh-keygen
# example pub
# paste it to https://github.com/settings/keys
cat .ssh/id_ed25519.pub

ssh -l leybovich-nikita 84.201.131.244
# e.g. git@github.com:potykion/potyk-io.git
git clone git@github.com:potykion/potyk-io.git

cd potyk-io
python3 -m venv ".venv"
source ./.venv/bin/activate
pip install -r requirements.txt
# fill env w FLASK_SECRET=...
# (локально: FLASK_APP=main:create_app для flask run)
nano .env

sudo cp ./ops/potyk-io.service /etc/systemd/system/potyk-io.service
sudo cp ./ops/potyk-io-backup.service /etc/systemd/system/potyk-io-backup.service
sudo cp ./ops/potyk-io-backup.timer /etc/systemd/system/potyk-io-backup.timer
sudo cp ./ops/potyk-tg.service /etc/systemd/system/potyk-tg.service
sudo chmod 644 /etc/systemd/system/potyk-io.service \
  /etc/systemd/system/potyk-io-backup.service \
  /etc/systemd/system/potyk-io-backup.timer \
  /etc/systemd/system/potyk-tg.service
sudo systemctl daemon-reload
sudo systemctl enable --now potyk-io.service
sudo systemctl enable --now potyk-io-backup.timer
sudo systemctl enable --now potyk-tg.service
# В .env нужны YC_S3_ACCESS_KEY / YC_S3_SECRET_KEY (бакет potyk-io-backups)

# Caddy (reverse proxy → :5008)
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy

# конфиг из репо (caddy должен уметь читать путь)
chmod o+x /home/leybovich-nikita
chmod 644 /home/leybovich-nikita/potyk-io/ops/Caddyfile
sudo ln -sf /home/leybovich-nikita/potyk-io/ops/Caddyfile /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl enable --now caddy
sudo systemctl reload caddy

```

### Update

```shell
ssh -l leybovich-nikita 84.201.131.244
cd potyk-io
git pull

source ./.venv/bin/activate
pip install -r requirements.txt 

sudo cp ./ops/potyk-io.service /etc/systemd/system/potyk-io.service
sudo cp ./ops/potyk-io-backup.service /etc/systemd/system/potyk-io-backup.service
sudo cp ./ops/potyk-io-backup.timer /etc/systemd/system/potyk-io-backup.timer
sudo cp ./ops/potyk-tg.service /etc/systemd/system/potyk-tg.service
sudo ln -sf /home/leybovich-nikita/potyk-io/ops/Caddyfile /etc/caddy/Caddyfile
sudo systemctl daemon-reload
sudo systemctl restart potyk-io.service
sudo systemctl enable --now potyk-io-backup.timer
sudo systemctl restart potyk-tg.service
sudo systemctl reload caddy
```

### Load db from prod to local 

```sh 
scp leybovich-nikita@84.201.131.244:/home/leybovich-nikita/potyk-io/instance/main.db instance/prod.db
```
