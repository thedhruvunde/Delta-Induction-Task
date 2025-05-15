addgroup g_user
addgroup g_mod
addgroup g_admin
addgroup g_author
apt update -y && apt install wget -y
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
