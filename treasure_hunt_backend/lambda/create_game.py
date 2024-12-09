import json
import boto3
import os

ssm = boto3.client('ssm', region_name=os.getenv('REGION'))


def lambda_handler(event, context):
    subscription_key = ssm.get_parameters(Names=['/treasurehunt/dev/subscription-key'], WithDecryption=True)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('This is create_game.py')
    }
