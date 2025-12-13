#!/bin/sh

false << "EOF" > /dev/null

bash scripts/ops/backup.sh -m cube-spot
EOF

# https://stackoverflow.com/a/34531699
m=cube
while getopts ":m:" opt; do
    case $opt in
        m)
        echo "-m was triggered, Parameter: $OPTARG" >&2
        m=$OPTARG
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


mkdir -p log/backup/
backup_path=log/backup/$m-`date +%Y-%m-%d-%Hh-%Mm`
echo $backup_path
# cp -r log/$m $backup_path
mv log/$m $backup_path
mv typescript $backup_path/stdout.ts
