
#!/usr/bin/env bash
set -euo pipefail

# run_test_batch.sh
# Usage: run_test_batch.sh <start_num> <count> [--sleep SECONDS] [--project-prefix PREFIX] [--dry-run]
#
# Example:
#   ./run_test_batch.sh 1 5 --sleep 600 --project-prefix wdt_dbg --dry-run

start_num=${1-}
count=${2-}

if [[ -z "$start_num" || -z "$count" ]]; then
	echo "Usage: $0 <start_num> <count> [--sleep SECONDS] [--project-prefix PREFIX] [--dry-run]"
	exit 2
fi

# Defaults
SLEEP_SECONDS=600
PROJECT_PREFIX="wdt_dbg"
DRY_RUN=0

shift 2

while [[ $# -gt 0 ]]; do
	case "$1" in
		--sleep)
			SLEEP_SECONDS="$2"
			shift 2
			;;
		--project-prefix)
			PROJECT_PREFIX="$2"
			shift 2
			;;
		--dry-run)
			DRY_RUN=1
			shift 1
			;;
		*)
			echo "Unknown arg: $1"
			exit 2
			;;
	esac
done

# Determine ADK_ROOT (use environment or infer from script path)
if [[ -z "${ADK_ROOT-}" ]]; then
	SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
	ADK_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
fi

echo "Starting batch run: start=$start_num count=$count prefix=$PROJECT_PREFIX sleep=$SLEEP_SECONDS dry_run=$DRY_RUN"

end_num=$((start_num + count - 1))

for i in $(seq "$start_num" "$end_num"); do
	proj_folder="${PROJECT_PREFIX}${i}"

	echo "\n=== Running test for project: $proj_folder (iteration $i) ==="

	run_test_cmd=("$ADK_ROOT/openspec-scripts/run_test.sh" "8051" "iflow/qwen3-coder-plus" "$proj_folder" "0,1")

	if [[ $DRY_RUN -eq 1 ]]; then
		echo "DRY RUN: ${run_test_cmd[*]}"
	else
		"${run_test_cmd[@]}"
	fi

	echo "Sleeping for $SLEEP_SECONDS seconds..."
	if [[ $DRY_RUN -eq 1 ]]; then
		echo "DRY RUN: sleep $SLEEP_SECONDS"
	else
		sleep "$SLEEP_SECONDS"
	fi

	if [[ -d "$proj_folder" ]]; then
		echo "Entering $proj_folder"
		if [[ $DRY_RUN -eq 1 ]]; then
			echo "DRY RUN: cd $proj_folder && $ADK_ROOT/openspec-scripts/run-meta-improve.sh --workdir ./adk_openspec_project"
		else
			pushd "$proj_folder" >/dev/null
			"$ADK_ROOT/openspec-scripts/run-meta-improve.sh" --workdir ./adk_openspec_project
			popd >/dev/null
		fi
	else
		echo "Warning: project folder '$proj_folder' does not exist. Skipping meta-improve step."
	fi

	echo "Sleeping for $SLEEP_SECONDS seconds..."
	if [[ $DRY_RUN -eq 1 ]]; then
		echo "DRY RUN: sleep $SLEEP_SECONDS"
	else
		sleep "$SLEEP_SECONDS"
	fi
done

echo "Batch run complete"