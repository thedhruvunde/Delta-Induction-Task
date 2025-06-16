git clone --branch Task-1 https://github.com/thedhruvunde/Delta-Induction-Task.git /scripts
export PATH="/scripts/apps:$PATH"
scrDir="/scripts/apps"
YAML_FILE="/scripts/templates/users.yaml"
INIT_SCRIPT="$scrDir/initUsers"
addgroup g_user
addgroup g_mod
addgroup g_admin
addgroup g_author
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
chmod +x /scripts/apps/*
cp "/scripts/templates/watchUsers.sh" "/usr/local/bin/watchUsers.sh"
cp "/scripts/templates/users-sync.service" "/etc/systemd/system/users-sync.service"
chmod +x /usr/local/bin/watchUsers.sh
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable users-sync.service
systemctl start users-sync.service
