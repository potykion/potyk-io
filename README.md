# potyk-io

> personal internet

## Links

- [Github](https://github.com/potykion/potyk-io.git)

## Prod Setup

- ВМ (Yandex Cloud): 2 vCPU (100%), 2 ГБ RAM, 20 ГБ диск, Intel Ice Lake.  
- Gunicorn: `workers=2` / `threads=4` / `gthread` — под 2 ядра и SQLite (см. `gunicorn.conf.py`).

### First

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

sudo cp ./potyk-io.service /etc/systemd/system/potyk-io.service
sudo chmod 644 /etc/systemd/system/potyk-io.service
sudo systemctl daemon-reload
sudo systemctl enable --now potyk-io.service

# Caddy (reverse proxy :80 → :5008, /fin → :5007)
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
chmod 644 /home/leybovich-nikita/potyk-io/Caddyfile
sudo ln -sf /home/leybovich-nikita/potyk-io/Caddyfile /etc/caddy/Caddyfile
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

sudo cp ./potyk-io.service /etc/systemd/system/potyk-io.service
sudo systemctl daemon-reload
sudo systemctl restart potyk-io.service
sudo systemctl reload caddy
```
