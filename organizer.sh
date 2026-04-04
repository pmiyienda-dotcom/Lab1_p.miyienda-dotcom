#!/usr/bin/env bash
# organizer.sh - Archive grades.csv, reset workspace, and log the operation.

set -euo pipefail

TARGET_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# 1. Ensure the archive directory exists
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo "Created directory: $ARCHIVE_DIR"
else
    echo "Archive directory already exists: $ARCHIVE_DIR"
fi

# 2. Check the source file exists
if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: '$TARGET_FILE' not found in the current directory. Nothing to archive."
    exit 1
fi

# 3. Generate timestamp
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

#4. Move and rename the file into the archive
mv "$TARGET_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"
echo "Archived: $TARGET_FILE  →  $ARCHIVE_DIR/$ARCHIVED_NAME"

# 5. Reset workspace with a fresh empty grades.csv
touch "$TARGET_FILE"
echo "Created fresh empty file: $TARGET_FILE"

#6. Append to log
{
    echo "Timestamp    : $TIMESTAMP"
    echo "Original File: $TARGET_FILE"
    echo "Archived As  : $ARCHIVE_DIR/$ARCHIVED_NAME"
} >> "$LOG_FILE"

echo "Log updated: $LOG_FILE"
echo "Done."
