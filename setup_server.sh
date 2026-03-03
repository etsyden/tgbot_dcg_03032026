#!/bin/bash

# Настройка сервера для Dental Clinic Bot
# Запускать как root на Ubuntu 22.04

set -e

DOMAIN="bot2.dentalcitygroup.ru"
EMAIL="admin@dentalcitygroup.ru" # Замените на реальный
PROJECT_DIR="/opt/tgbot"

echo "--- Installing dependencies ---"
apt update
apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git postgresql postgresql-contrib

echo "--- Setting up directory ---"
mkdir -p $PROJECT_DIR
chown $USER:$USER $PROJECT_DIR

if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "--- Cloning repo ---"
    git clone https://github.com/etsyden/tgbot_dcg_03032026.git $PROJECT_DIR
fi

cd $PROJECT_DIR

echo "--- Setting up venv ---"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "--- Configuring Nginx ---"
cat > /etc/nginx/sites-available/tgbot <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files for admin
    location /static {
        alias $PROJECT_DIR/app/admin/static;
    }
}
EOF

ln -sf /etc/nginx/sites-available/tgbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

echo "--- Issuing SSL Certificate ---"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL

echo "--- Configuring Systemd Service ---"
cat > /etc/systemd/system/tgbot.service <<EOF
[Unit]
description=Gunicorn instance to serve Dental Clinic Bot
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable tgbot
systemctl start tgbot

echo "--- DONE! ---"
echo "Don't forget to setup .env file and GitHub Secrets (SSH_HOST, SSH_USER, SSH_PRIVATE_KEY)"
