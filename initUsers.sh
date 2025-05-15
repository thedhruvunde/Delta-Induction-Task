#!/bin/bash
home_dirs=("admin" "users" "mods" "authors")
for dir in "${home_dirs[@]}"; do
    mkdir -p "/home/$dir"
    echo "$dir directory created"
done

CONFIG_FILE="/scripts/templates/users.yaml"


create_user() {
    local username=$1
    local home_dir=$2
    local group_name=$3

    if id "$username" &>/dev/null; then
        echo "User $username already exists!"
    else
        useradd -m -d "$home_dir" "$username"
        usermod -a -G $group_name $username
        echo "User $username created!"
    fi
}
get_usernames() {
    yq ".${1}[].username" "$CONFIG_FILE" | sort -u
}

get_authors() {
    yq '.mods[] | select(.username == "'"$1"'") | .authors[]' users.yaml
}

echo "Processing Admins..."
get_usernames "admins" | while read -r username; do
    home="/home/admin/$username"
    create_user "$username" "$home" "g_admin"
done

echo "Processing Users..."
get_usernames "users" | while read -r username; do
    home="/home/users/$username"
    create_user "$username" "$home" "g_user"
    mkdir -p "/home/users/$username/all_blogs"
done

echo "Processing Authors..."
get_usernames "authors" | while read -r username; do
    home="/home/authors/$username"
    create_user "$username" "$home" "g_author"
done

author_dirs=("blogs" "public")
get_usernames "authors" | while read -r username; do
    for dir in "${author_dirs[@]}"; do
		mkdir -p "/home/authors/$username/$dir"
    done
    cp "blogs.yaml" "/home/authors/$username/"
done


echo "Processing Moderators..."
get_usernames "mods" | while read -r username; do
    home="/home/mods/$username"
    create_user "$username" "$home" "g_mod"
done

echo "Processing User permissions..."
get_usernames "users" | while read -r username; do
    home="/home/users/$username"
    chmod 700 $home
done

echo "Processing admin permissions..."
get_usernames "admins" | while read -r username; do
    home="/home/admin/$username"
    chmod 700 $home
    usermod -a -G sudo $username
done

echo "Processing Moderators permissions..."
get_usernames "mods" | while read -r modid; do
    home="/home/mods/$modid"
    chmod 700 $home
    get_authors $modid | while read -r authorid; do
        usermod -a -G $authorid $modid
        chown $authorid:$authorid "/home/authors/$authorid"
        chmod 770 "/home/authors/$authorid"
        mkdir -p "/home/mods/$modid/AuthorDirs/$authorid"
        cp "/scripts/templates/blacklist.txt" "$home"
        ln -s "/home/authors/$authorid" "/home/mods/$modid/AuthorDirs/$authorid"
    done
done


echo "Creating all_blogs symlinks for users..."
authors=$(get_usernames "authors")
get_usernames "users" | while read -r user; do
    allBlogsDir="/home/users/$user/all_blogs"
    mkdir -p "$allBlogsDir"
    for author in $authors; do
        target="/home/authors/$author/public"
        linkname="$allBlogsDir/$author"
        ln -s "$target" "$linkname"
    done
    chmod 500 "$allBlogsDir"
    chmod -R 500 "$allBlogsDir"/*
    echo "All blog links created for user: $user"
done
getExistingUsersInGroup() {
    getent group "$1" | cut -d: -f4 | tr ',' '\n' | sort -u
}

syncUsersInGroup() {
    role=$1
    group=$2

    existingUsers=$(getExistingUsersInGroup "$group")
    yamlUsers=$(get_usernames "$role")

    for user in $existingUsers; do
        if ! grep -qx "$user" <<< "$yamlUsers"; then
            echo "Removing $user from group '$group' (not in '$role')"
            current_groups=$(id -nG "$user" | tr ' ' '\n' | grep -v "^$group$" | paste -sd, -)
            sudo usermod -G "$current_groups" "$user"
        fi
    done
}

syncUsersInGroup "users" "g_user"
syncUsersInGroup "authors" "g_author"
syncUsersInGroup "mods" "g_mod"
syncUsersInGroup "admins" "g_admin"

echo "Updating moderators' author access..."
get_usernames "mods" | while read -r mod; do
    echo "Resetting author groups for moderator: $mod"
    current_groups=$(id -nG "$mod")
    new_groups=""
    for group in $current_groups; do
        if ! get_usernames "authors" | grep -qx "$group"; then
            new_groups+="$group "
        fi
    done
    usermod -G "$new_groups" "$mod"
    yq ".mods[] | select(.username == \"$mod\") | .authors[]" "$CONFIG_FILE" | while read -r authorname; do
        echo "Granting $mod access to $authorname"
        usermod -a -G "$authorname" "$mod"
        chown "$authorname:$authorname" "/home/authors/$authorname/public"
        chmod 770 "/home/authors/$authorname"
    done
done
