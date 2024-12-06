import aws_cdk as core
import aws_cdk.assertions as assertions

from treasure_hunt_backend.treasure_hunt_backend_stack import TreasureHuntBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in treasure_hunt_backend/treasure_hunt_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TreasureHuntBackendStack(app, "treasure-hunt-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
