#!/usr/bin/env bash
set -euo pipefail

scenario_path="${SCENARIO_PATH:-}"
if [[ -z "${scenario_path// }" ]]; then
    echo "ERROR: SCENARIO_PATH is required. Set it to the composed scenario folder before running this pattern." >&2
    exit 1
fi

if [[ ! -d "$scenario_path" ]]; then
    echo "ERROR: Scenario folder not found: $scenario_path" >&2
    exit 1
fi

manifest_path="$scenario_path/manifest.json"
if [[ ! -f "$manifest_path" ]]; then
    echo "ERROR: Scenario manifest not found: $manifest_path" >&2
    exit 1
fi

for key in host welcome catalog presentation; do
    if ! python3 -c "import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if sys.argv[2] in d else 1)" "$manifest_path" "$key"; then
        echo "ERROR: Scenario manifest is missing required key '$key' (see config/scenario-config.schema.json)." >&2
        exit 1
    fi
done

echo "Scenario folder: $scenario_path"
echo "Scenario manifest validated against the required config keys: host, welcome, catalog, presentation."
