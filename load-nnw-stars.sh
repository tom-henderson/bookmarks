#!/bin/bash

# Database file
DB_FILE="/Users/tom/Library/Containers/com.ranchero.NetNewsWire-Evergreen/Data/Library/Application Support/NetNewsWire/Accounts/16_F5A95C39-4008-4338-B77D-F28949D6FA3F/DB.sqlite3"
API_URL="http://0.0.0.0:8000/api/new/"
API_TOKEN="3bd02a4b8d405d05b7f5948fb06f4449fd22d734"
TAGS="stars"
PRIVATE="true"

# SQLite query to retrieve data
SQL_QUERY="SELECT a.title, a.externalURL, 
           DATETIME(ROUND(a.datePublished), 'unixepoch') AS published, 
           DATETIME(ROUND(s.dateArrived), 'unixepoch') AS starred 
           FROM articles a 
           JOIN statuses s ON a.articleID = s.articleID 
           WHERE s.starred = 1;"

format_date() {
    date -j -f "%Y-%m-%d %H:%M:%S" "$1" "+%Y-%m-%dT%H:%M"
}

format_description() {
    # Remove HTML
    # If longer than a certain length, return summarized
}

# Function to send data using curl
post_data() {
    local title="$1"
    local url="$2"
    local date_added="$3"
    # local description="$4"
    curl -v $API_URL -H "Authorization: Token $API_TOKEN" -d "title=$title&url=$url&date_added=$date_added&tags=$TAGS"
    # curl -v $API_URL -H "Authorization: Token $API_TOKEN" -d "title=$title&url=$url&date_added=$date_added&tags=$TAGS&description=$description"
}

# Display the data with colored formatting
print_data() {
    echo -e "Title: $1"
    echo -e "URL: $2"
    echo -e "Published: $3"
    echo -e "Starred: $4"
    # echo -e "Description: $5"
}

# Redirect stdin to another file descriptor so it doesn't interfere with `read`
exec 3<&0

# Fetch data from sqlite and process each row individually
sqlite3 "$DB_FILE" "$SQL_QUERY" | while read -r line; do
    title=$(echo "$line" | awk -F'|' '{print $1}')
    externalURL=$(echo "$line" | awk -F'|' '{print $2}')
    published=$(echo "$line" | awk -F'|' '{print $3}')
    starred=$(echo "$line" | awk -F'|' '{print $4}')

    # Display the data with colored formatting
    print_data "$title" "$externalURL" "$published" "$starred"

    # Prompt user for input
    read -p "Proceed? y/n: " proceed <&3
    if [[ "$proceed" == "y" ]]; then
        # Format starred date as needed

        # YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
        # 2024-04-02T06:27
        date_added=$(format_date "$starred")
        
        echo "Saving"
        # Post the data
        post_data "$title" "$externalURL" "$date_added"
    else
        echo "Skipping"
    fi

    echo
done