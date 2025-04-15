#!/bin/bash
if [ $# -eq 0 ];
then
  echo "$0: Missing datapipeline run ID argument"
  exit 1
elif [ $# -gt 1 ];
then
  echo "$0: Too many arguments: $@"
  exit 1
else
  echo "We got some argument(s)"
  echo "==========================="
  echo "Number of arguments.: $#"
  echo "List of arguments...:"
  echo "Datapipeline ID:..............: $1"
  echo "==========================="
fi
datapipeline_id=$1
echo "activating pipeline..."
aws datapipeline activate-pipeline --pipeline-id ${datapipeline_id}
echo "Get the pipeline object id that needs to be re-ran"
aws datapipeline list-runs --pipeline-id ${datapipeline_id} --region eu-west-1 | grep "@ImportTime_" > Object_id.txt
object_id=$(awk '{print $1}' Object_id.txt)
echo "Re-running the ${datapipeline_id} datapipeline"
aws datapipeline set-status --pipeline-id ${datapipeline_id} --status RERUN --object-ids ${object_id} --region eu-west-1
echo "${datapipeline_id} is now running"
aws datapipeline list-runs --pipeline-id ${datapipeline_id} --region eu-west-1
echo "exiting script...."
