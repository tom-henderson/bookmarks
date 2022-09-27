#!/bin/bash
set -e
set -o pipefail

TAG="$1"

if [[ -z "$GITHUB_TOKEN" ]]; then
	echo "ERROR: GITHUB_TOKEN env variable is not set."
	exit 1
fi

if [[ -z "$GITHUB_REPOSITORY" ]]; then
	echo "ERROR: GITHUB_REPOSITORY env variable is not set."
	exit 1
fi

function slack_notification() {
	MESSAGE=$1

	PAYLOAD="'text':'${MESSAGE}'"

	if [[ -z "$SLACK_WEBHOOK_URL" ]]; then
		echo "INFO: SLACK_WEBHOOK_URL env variable is not set, notifications will not be sent."
		return
	fi

	if [[ -n "$SLACK_CHANNEL" ]]; then
		PAYLOAD="${PAYLOAD},'channel':'${SLACK_CHANNEL}'"
	fi

	echo "INFO: Sending slack message ${MESSAGE}."
	curl --silent --output /dev/null --show-error --request POST --header 'Content-type: application/json' --data "{${PAYLOAD}}" "${SLACK_WEBHOOK_URL}"
}

GITHUB_API_URI=https://api.github.com
API_VERSION=v3
API_HEADER="Accept: application/vnd.github.${API_VERSION}+json"
AUTH_HEADER="Authorization: token ${GITHUB_TOKEN}"

HEAD=$(jq --raw-output .after "$GITHUB_EVENT_PATH")
PAYLOAD=$(cat <<EOF
{
	"tag": "${TAG}",
	"object": "${HEAD}",
	"message": "${TAG}",
	"type": "commit"
}
EOF
)

echo "event payload:"
echo $PAYLOAD

echo "creating tag object"
TAG_OBJECT=$(curl --request POST -sSL \
				  --header "${AUTH_HEADER}" \
				  --header "${API_HEADER}" \
				  --header 'Content-type: application/json' \
				  --data "${PAYLOAD}" \
				  "${GITHUB_API_URI}/repos/${GITHUB_REPOSITORY}/git/tags"
)
echo ${TAG_OBJECT}
echo "finding tag sha"
TAG_OBJECT_SHA=$(echo $TAG_OBJECT | jq .object.sha --raw-output)
PAYLOAD=$(cat <<EOF
{
  "ref": "refs/tags/${TAG}",
  "sha": "${TAG_OBJECT_SHA}"
}
EOF
)

echo "creating tag ref"
curl --request POST -sSL \
	 --header "${AUTH_HEADER}" \
	 --header "${API_HEADER}" \
	 --header 'Content-type: application/json' \
	 --data "${PAYLOAD}" \
	 "${GITHUB_API_URI}/repos/${GITHUB_REPOSITORY}/git/refs"

slack_notification ":label: \`${GITHUB_REPOSITORY}\` tagged \`${TAG}\`"

if [[ -n "$GIF_KEYWORD" ]]; then
	GIF=$(curl -s "http://curated-ship-gifs.petegoo.com/search?q=${GIF_KEYWORD}" | jq --raw-output .data.image_url)
	if [[ -n "$GIF" ]]; then
		slack_notification "$GIF"
	fi
fi
