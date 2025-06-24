export PATH="/scripts/apps/:$PATH"
scrDir="/scripts/apps"
YAML_FILE="/scripts/templates/users.yaml"
INIT_SCRIPT="$scrDir/initUsers"
CRON_TIME="14 15 * 2,5,8,11 4,6"
REPORT_SCRIPT="/scripts/apps/adminPanel"
CRON_CMD="$CRON_TIME $REPORT_SCRIPT"
addgroup g_user
addgroup g_mod
addgroup g_admin
addgroup g_author
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
chmod +x /scripts/apps/*
cp "/scripts/templates/watchUsers" "/usr/local/bin/watchUsers"
cp "/scripts/templates/countReads" "/usr/local/bin/countReads"
cp "/scripts/templates/users-sync.service" "/etc/systemd/system/users-sync.service"
cp "/scripts/templates/count-reads.service" "/etc/systemd/system/count-reads.service"
chmod +x /usr/local/bin/watchUsers
chmod +x /usr/local/bin/countReads
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable users-sync.service
systemctl start users-sync.service
systemctl enable count-reads.service
systemctl start count-reads.service
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
ln -s /etc/nginx/sites-available/nginx-config /etc/nginx/sites-enabled/
nginx -t >> /dev/null
systemctl reload nginx
chmod +x /db/init-db.sh
PGPASSWORD=hackjack psql -U hyphen -d coolblogsdb -h db -c "
CREATE TABLE IF NOT EXISTS blogs (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    author VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('published', 'archived', 'deleted')),
    category_order INTEGER[],
    publish_date DATE,
    read_count INTEGER DEFAULT 0,
    moderator VARCHAR(50),
    mod_comments TEXT,
);"
