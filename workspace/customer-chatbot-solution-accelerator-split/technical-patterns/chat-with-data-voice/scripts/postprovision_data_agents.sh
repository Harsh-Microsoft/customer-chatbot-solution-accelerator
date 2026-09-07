#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

upload_ok=1
bash "$HERE/run_data_upload.sh" || upload_ok=0
if [[ $upload_ok -eq 0 ]]; then
  echo "Upload data script failed." >&2
fi

echo ""
echo ""

agents_ok=1
bash "$HERE/run_agents.sh" || agents_ok=0
if [[ $agents_ok -eq 0 ]]; then
  echo "Create agents script failed." >&2
fi

echo ""

if [[ $upload_ok -eq 0 || $agents_ok -eq 0 ]]; then
  echo "One or more post-provision scripts failed. Please check the logs above for details." >&2

  if [[ $upload_ok -eq 0 ]]; then
    echo "" >&2
    echo "To retry the upload data script, run the following command:" >&2
    echo "    bash ./scripts/run_data_upload.sh" >&2
  fi

  if [[ $agents_ok -eq 0 ]]; then
    echo "" >&2
    echo "To retry the create agents script, run the following command:" >&2
    echo "    bash ./scripts/run_agents.sh" >&2
  fi

  exit 1
fi

CHAT_WEB_APP_URL=$(azd env get-value CHAT_WEB_APP_URL)
SCENARIO_WEB_APP_URL=$(azd env get-value SCENARIO_WEB_APP_URL)

echo ""
echo "Post-Deployment scripts completed successfully."
echo "You can now access the Chat Web App and Scenario Web App using the following URLs:"
echo ""
echo "  Chat Web App URL: $CHAT_WEB_APP_URL"
echo "  Scenario Web App URL: $SCENARIO_WEB_APP_URL"
