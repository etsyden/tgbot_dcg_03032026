#!/bin/bash

# Настройка сервера для Dental Clinic Bot
# Запускать как root на Ubuntu 22.04

set -e

DOMAIN="bot2.dentalcitygroup.ru"
EMAIL="admin@dentalcitygroup.ru"
PROJECT_DIR="/opt/tgbot"

echo "--- Installing dependencies ---"
apt-get update
apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git postgresql postgresql-contrib

echo "--- Setting up directory ---"
mkdir -p $PROJECT_DIR

if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "--- Cloning repo ---"
    git clone https://github.com/etsyden/tgbot_dcg_03032026.git $PROJECT_DIR
fi

cd $PROJECT_DIR

echo "--- Setting up venv ---"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

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
# Мы запускаем certbot. Если он не сможет выпустить сертификат (например, из-за DNS), скрипт не упадет.
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL || echo "Certbot failed, check DNS and firewall"

echo "--- Configuring Systemd Service ---"
cat > /etc/systemd/system/tgbot.service <<EOF
[Unit]
Description=Gunicorn instance to serve Dental Clinic Bot
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
# Ensure .env exists or this might fail
ExecStartPre=/usr/bin/touch $PROJECT_DIR/.env
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable tgbot
systemctl start tgbot || echo "Service failed to start, check .env file"

echo "--- DONE! ---"
