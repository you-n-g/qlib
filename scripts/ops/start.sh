#!/bin/sh

m=cube
resume=0
remove_previous=0
custom=1
while getopts ":m:rRc" opt; do
    case $opt in
        m)
        echo "-m was triggered, specified competition: $OPTARG" >&2
        m=$OPTARG
        ;;
        r)
        echo "-r was triggered, resuming from last session." >&2
        resume=1
        ;;
        R)
        echo "-R was triggered, removing previous session." >&2
        remove_previous=1
        ;;
        c)
        echo "-c was triggered, custom proposal." >&2
        custom=1
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

LOG_TRACE_PATH=./log/$m


CMD="LOG_TRACE_PATH=$LOG_TRACE_PATH mydotenv.sh python -m ipdb -c c  rdagent/app/data_science/loop.py --competition $m"

if [ $resume -eq 1 ]; then
    echo "Resuming from last session."
    CMD="$CMD --path $LOG_TRACE_PATH"
elif [ -e $LOG_TRACE_PATH ]; then
    if [ $remove_previous -eq 1 ]; then
        echo "Log path $LOG_TRACE_PATH already exists. Removing previous session."
        rm -r $LOG_TRACE_PATH
    else
      echo "Log path $LOG_TRACE_PATH already exists. Exiting."
      exit 1
    fi
fi

if [ $custom -eq 1 ]; then
    CMD="$CMD --exp_gen_cls rdagent.scenarios.data_science.proposal.exp_gen.custom.CustomExpGen"
fi

script -c "$CMD"
