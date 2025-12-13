#!/bin/bash

false << "EOF" > /dev/null
bash ./scripts/tasks/expand_inst.sh -p /Data/home/xiaoyang/repos/RD-Agent-QUBE3/log/cube-spot/  -e 132 -o log/cube-spot/
EOF

out_path=log/cube/

# https://stackoverflow.com/a/34531699
while getopts ":p:e:o:" opt; do
    case $opt in
        p)
        echo "-p was triggered, Parameter: $OPTARG" >&2
        path="$OPTARG"
        ;;
        e)
        echo "-e was triggered. end_idx: $OPTARG" >&2 
        end_idx=$OPTARG
        ;;
        o)
        echo "-o was triggered. out_path: $OPTARG" >&2
        out_path=$OPTARG
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

if [ -z "$path" ]; then
    echo "Error: -p PATH is required." >&2
    exit 1
fi

# for config

mydotenv.sh python scripts/ts/run_spot.py
mydotenv.sh python scripts/ops/conf/timeout.py --debug-hours 1.0 --full-hours 4.0
# mydotenv.sh python scripts/ops/conf/fix_intention.py set-intention "Please include a broader range of instruments in the data, for example, the top 50 by trading volume. Since we now have longer time limits compared with the previous best solution, you can make use of additional computational resources."
mydotenv.sh python scripts/ops/conf/fix_intention.py set-intention "Please include a broader range of instruments in the data, for example, the top 30 by trading volume. Don't try to compromise on the method design for the sake of computational efficiency."


# for run
mydotenv.sh python scripts/create_session.py $path -e $end_idx -f  -o $out_path

bash scripts/ops/start.sh -r -c  -m `basename $out_path`
