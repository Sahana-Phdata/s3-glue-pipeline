import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

glue = boto3.client("glue")

WORKFLOW_NAME = os.environ["WORKFLOW_NAME"]


def lambda_handler(event, context):

    logger.info("Received S3 event: %s", event)

    response = glue.start_workflow_run(
        Name=WORKFLOW_NAME
    )

    workflow_run_id = response["RunId"]

    logger.info(
        "Started Glue Workflow: %s, Run ID: %s",
        WORKFLOW_NAME,
        workflow_run_id
    )

    return {
        "statusCode": 200,
        "workflowName": WORKFLOW_NAME,
        "workflowRunId": workflow_run_id
    }