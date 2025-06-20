git clone --branch Task-1 https://github.com/thedhruvunde/Delta-Induction-Task.git /scripts
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
