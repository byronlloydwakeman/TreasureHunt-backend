from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam
)
from constructs import Construct


class TreasureHuntBackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        environment = self.node.try_get_context("env") or "dev"

        table_pk = "game_instance_id"
        table_sk = "timestamp"

        # DynamoDB Table
        table_name = f"TreasureHuntTable-{environment}"
        table = dynamodb.Table(
            self,
            "TreasureHuntTable",
            table_name=table_name,
            partition_key=dynamodb.Attribute(
                name=table_pk, type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name=table_sk, type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        lambda_dir = "treasure_hunt_backend/lambda"

        # Lambda Function: Create Game Instance
        create_game_lambda = lambda_.Function(
            self,
            "CreateGameLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="create_game.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir),
            environment={
                "TABLE_NAME": table_name,
                "ENVIRONMENT": environment,
            },
            function_name=f"CreateGameLambda-{environment}"
        )

        # Lambda Function: Read Game Instance
        read_game_lambda = lambda_.Function(
            self,
            "ReadGameLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="read_game.lambda_handler",
            code=lambda_.Code.from_asset(lambda_dir),
            environment={
                "TABLE_NAME": table_name,
                "ENVIRONMENT": environment,
            },
            function_name=f"ReadGameLambda-{environment}"
        )

        lambdaSSMAccess = iam.PolicyStatement(
            actions=[
                "ssm:GetParameter",  # For single parameters
                "ssm:GetParameters",  # For multiple parameters
            ],
            resources=[
                f"arn:aws:ssm:{self.region}:{self.account}:parameter/*",  # All parameters
            ]
        )

        lambdaKMSAccess = iam.PolicyStatement(
            actions=["kms:Decrypt"],
            resources=[f"arn:aws:kms:{self.region}:{self.account}:key/09a58808-d99a-4f1d-b2eb-2da1e1c53ee3"]
        )

        # Grant DynamoDB access to Lambda functions
        table.grant_read_write_data(create_game_lambda)
        table.grant_read_write_data(read_game_lambda)

        create_game_lambda.add_to_role_policy(lambdaSSMAccess)
        create_game_lambda.add_to_role_policy(lambdaKMSAccess)

        read_game_lambda.add_to_role_policy(lambdaSSMAccess)
        read_game_lambda.add_to_role_policy(lambdaKMSAccess)

        # Lambda Aliases
        create_game_alias = lambda_.Alias(
            self,
            "CreateGameAlias",
            alias_name=environment,
            version=create_game_lambda.current_version,
        )

        read_game_alias = lambda_.Alias(
            self,
            "ReadGameAlias",
            alias_name=environment,
            version=read_game_lambda.current_version,
        )

        # SQS
        queue = sqs.Queue(
            self,
            "TreasureHuntQueue",
            visibility_timeout=Duration.seconds(300),
        )
