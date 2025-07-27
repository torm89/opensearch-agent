import os
import time
from argparse import ArgumentParser
from typing import Optional

import boto3


def create_agent_runtime(client, runtime_name, image_uri, network_configuration, role_arn):
    response = client.create_agent_runtime(
        agentRuntimeName=runtime_name,
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': image_uri
            }
        },
        networkConfiguration=network_configuration,
        roleArn=role_arn
    )

    return {
        'agentRuntimeId': response['agentRuntimeId'],
        'agentRuntimeArn': response['agentRuntimeArn'],
    }


def update_agent_runtime(client, runtime_id, image_uri, network_configuration, role_arn):
    response = client.update_agent_runtime(
        agentRuntimeId=runtime_id,
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': image_uri
            }
        },
        networkConfiguration=network_configuration,
        roleArn=role_arn
    )

    return {
        'agentRuntimeId': response['agentRuntimeId'],
        'agentRuntimeArn': response['agentRuntimeArn'],
    }


def check_agent_runtime_exists(client, runtime_name) -> Optional[str]:
    arguments = {}
    for _ in range(1000):
        response = client.list_agent_runtimes(**arguments)
        for runtime in response['agentRuntimes']:
            if runtime['agentRuntimeName'] == runtime_name:
                return runtime["agentRuntimeId"]
        arguments['nextToken'] = response.get('nextToken')
        if not arguments['nextToken']:
            return None

    raise Exception(f"Agent Runtime {runtime_name} not found after 1000 retries")


def get_agent_runtime_status(client, runtime_id):
    response = client.get_agent_runtime(agentRuntimeId=runtime_id)
    return response['status']


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--agent-runtime-name', type=str, required=True)
    parser.add_argument('--agent-runtime-image-uri', type=str, required=True)
    parser.add_argument('--agent-runtime-role-arn', type=str, required=True)

    args = parser.parse_args()

    agent_runtime_name = args.agent_runtime_name
    agent_runtime_image_uri = args.agent_runtime_image_uri
    agent_runtime_role_arn = args.agent_runtime_role_arn

    agent_network_configuration = {
        "networkMode": "PUBLIC"
    }

    client = boto3.client('bedrock-agentcore-control', region_name=os.environ['AWS_DEPLOYMENT_REGION_NAME'])

    agent_runtime_id = check_agent_runtime_exists(client, agent_runtime_name)

    if agent_runtime_id:
        print(f"Agent Runtime {agent_runtime_name} already exists. Updating...")
        agent_runtime = update_agent_runtime(
            client, agent_runtime_id, agent_runtime_image_uri, agent_network_configuration, agent_runtime_role_arn)
    else:
        print(f"Agent Runtime {agent_runtime_name} does not exist. Creating...")
        agent_runtime = create_agent_runtime(
            client, agent_runtime_name, agent_runtime_image_uri, agent_network_configuration, agent_runtime_role_arn)

    agent_runtime_id = agent_runtime['agentRuntimeId']
    agent_runtime_arn = agent_runtime['agentRuntimeArn']

    os.environ['AWS_BEDROCK_AGENT_RUNTIME_ID'] = agent_runtime_id
    os.environ['AWS_BEDROCK_AGENT_RUNTIME_ARN'] = agent_runtime_arn

    for _ in range(1000):
        agent_runtime_status = get_agent_runtime_status(client, agent_runtime_id)

        if agent_runtime_status == "READY":
            print(f"Agent Runtime {agent_runtime_name} is ready.")
            break
        elif agent_runtime_status == "CREATING":
            print(f"Agent Runtime {agent_runtime_name} is still creating. Waiting...")
            time.sleep(10)
        elif agent_runtime_status == "UPDATING":
            print(f"Agent Runtime {agent_runtime_name} is still updating. Waiting...")
            time.sleep(10)
        else:
            raise Exception(f"Unknown agent runtime status: {agent_runtime_status}")
