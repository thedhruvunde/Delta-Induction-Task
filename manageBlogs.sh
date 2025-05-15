#!/bin/bash

p_flag=""
a_flag=""
d_flag=""
e_flag=""
catl=""
authorid=$USER
AUTHOR_HOME="/home/authors/$AUTHOR"
BLOGS_DIR="$AUTHOR_HOME/blogs"
PUBLIC_DIR="$AUTHOR_HOME/public"
BLOG_CONFIG="/home/authors/$authorid/blogs.yaml"

get_categories() {
    yq '.categories[]' "$BLOG_CONFIG" | sort -u
}

while getopts "p:a:d:e:" opt; do
  case $opt in
    p)
        p_flag=$OPTARG
        echo "Enter Categories in which the blog belongs: "
        read catl
        yq -i ".blogs += [{"file_name": "$p_flag", "publish_status": true, "cat_order": $catl}]" $BLOG_CONFIG
        ln -s "$p_flag" "$HOME/public/$p_flag"
        chmod o+r "$BLOGS_DIR/$p_flag"
        ;;
    a)
        a_flag=$OPTARG
        echo "Archiving blog..."
        rm "$HOME/public/$a_flag"
        bindex=$(yq ".blogs | to_entries | map(select(.value.file_name == "$a_flag")) | .[0].key" $BLOG_CONFIG)
        yq -i ".blogs[$bindex].publish_status = false" $BLOG_CONFIG
        chmod o-r "$BLOGS_DIR/$a_flag"
        ;;
    d)
        d_flag=$OPTARG
        echo "Deleting blog..."
        rm "$HOME/public/$d_flag"
        rm "$HOME/blogs/$d_flag"
        bindex=$(yq ".blogs | to_entries | map(select(.value.file_name == "$d_flag")) | .[0].key" $BLOG_CONFIG)
        yq -i "del(.blogs[$bindex])" $BLOG_CONFIG
        ;;
    e)
        e_flag=$OPTARG
        echo "Enter the order of categories"
        i=1
        get_categories | while read -r category; do
            echo "$i -> $category"
            ((i++))
        done
        read cats
        bindex=$(yq ".blogs | to_entries | map(select(.value.file_name == "$e_flag")) | .[0].key" $BLOG_CONFIG)
        yq -i ".blogs[$bindex].cat_order = $cats" $BLOG_CONFIG
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
  esac
done
