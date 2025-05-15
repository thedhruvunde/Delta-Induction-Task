#!/bin/bash
BLACKLIST_FILE="/home/mods/$USER/blacklist.txt"
while getopts "f:" opt; do
  case $opt in
    f)
        INPUT_FILE=$OPTARG

        filename=$(basename "$INPUT_FILE")
        total_matches=0
        declare -A STAR_MAP
        while IFS= read -r word || [[ -n "$word" ]]; do
            [[ -z "$word" ]] && continue
            STAR_MAP["$word"]=$(printf '%*s' "${#word}" '' | tr ' ' '*')
        done < "$BLACKLIST_FILE"
        line_no=0
        temp_output=$(mktemp)

        while IFS= read -r line || [[ -n "$line" ]]; do
            ((line_no++))
            modified_line="$line"

            for word in "${!STAR_MAP[@]}"; do
                matches=$(echo "$line" | grep -ino "$word")

                if [[ -n "$matches" ]]; then
                    while IFS= read -r match; do
                        echo "Found blacklisted word $word in $INPUT_FILE at line $line_no"
                        ((total_matches++))

                    done <<< "$matches"

                    modified_line=$(echo "$modified_line" | sed "s/$word/${STAR_MAP[$word]}/gI")
                fi
            done

            echo "$modified_line" >> "$temp_output"
        done < "$INPUT_FILE"

        if (( total_matches > 5 )); then
            echo "Blog $INPUT_FILE is archived due to excessive blacklisted words."
            pubDir=$(dirname $INPUT_FILE)
            homDir=$(dirname $pubDir)
            shortcutFile="${homDir%/}/$(basename $INPUT_FILE)"
            BLOG_CONFIG="${homDir%/}/blogs.yaml"
            rm "$shortcutFile"
            bindex=$(yq ".blogs | to_entries | map(select(.value.file_name == "$(basename $INPUT_FILE)")) | .[0].key" $BLOG_CONFIG)
            yq -i ".blogs[$bindex].publish_status = false" $BLOG_CONFIG
            yq -i ".blogs[$bindex].mod_comments = found $total_matches blacklisted words"

        fi
        cp "$temp_output" "$INPUT_FILE"
        rm "$temp_output"
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
