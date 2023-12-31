from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
)


class CdkFolderStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        requests_layer = lambda_.LayerVersion(
            self,
            "MyLayer",
            code=lambda_.Code.from_asset("../requests-layer.zip"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11]
        )

        # Create our lambda Function
        my_lambda = lambda_.Function(self, "Premier-Web-Scraper",
                                      handler='Main.lambda_handler',
                                      runtime=lambda_.Runtime.PYTHON_3_11,
                                      layers=[requests_layer],
                                      code=lambda_.Code.from_asset('../web-scraper.zip'),
                                      timeout=Duration.minutes(10)
                                      )
        
        # Give S3 permissions to lambda function
        my_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:*",
                "s3-object-lambda:*"
            ],
            resources=[
                '*',
            ],
        ))

        # Create an EventBridge (CloudWatch Events) Trigger for every day at 6:00am UTC (1:00am EST)
        rule = events.Rule(
            self,
            "DailyRule",
            schedule=events.Schedule.cron(minute='0', hour='6'),
        )

        # Add the Lambda function as a target to the rule
        rule.add_target(targets.LambdaFunction(my_lambda))
