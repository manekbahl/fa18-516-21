import graphene
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import AWS as AwsModel
from models import Azure as AzureModel
from database import init_aws, init_azure

class AWS(MongoengineObjectType):
    class Meta:
        model = AwsModel
        interfaces = (Node,)

class Azure(MongoengineObjectType):
    class Meta:
        model = AzureModel
        interfaces = (Node,)

class Query(graphene.ObjectType):
    node = Node.Field()
    allAwss = MongoengineConnectionField(AWS)
    allAzures = MongoengineConnectionField(Azure)
    fetchAWSData = graphene.String()
    fetchAzureData = graphene.String()

    def resolve_fetchAWSData(self, info):
        init_aws()
        return "Success"
    
    def resolve_fetchAzureData(self, info):
        init_azure()
        return "Success"

class UpdateAws(graphene.Mutation):
    class Arguments:
        host = graphene.String()
        action = graphene.String()
        value = graphene.String()

    aws = graphene.Field(AWS)

    def mutate(self, info, host, action, value):
        if action == "stop":
            action = "state"
            value = "stopped"
        elif action == "shutdown":
            action = "state"
            value = "terminated"
        elif not action == "favorite":
            action = "state"
            value = "running"

        aws = AwsModel.objects.get(host=host)
        aws[action] = value
        aws.save()
        return UpdateAws(aws=aws)

class UpdateAzure(graphene.Mutation):
    class Arguments:
        host = graphene.String()
        action = graphene.String()
        value = graphene.String()

    azure = graphene.Field(Azure)

    def mutate(self, info, host, action, value):
        if action == "stop":
            action = "state"
            value = "Stopped"
        elif action == "shutdown":
            action = "state"
            value = "Deallocated"
        elif not action == "favorite":
            action = "state"
            value = "Running"

        azure = AzureModel.objects.get(host=host)
        azure[action] = value
        azure.save()
        return UpdateAzure(azure=azure)

class Mutation(graphene.ObjectType):
    update_aws = UpdateAws.Field()
    update_azure = UpdateAzure.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, types=[AWS, Azure])