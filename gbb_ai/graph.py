from configparser import SectionProxy

from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import \
    UserItemRequestBuilder


class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings["clientId"]
        tenant_id = self.settings["tenantId"]
        graph_scopes = self.settings["graphUserScopes"].split(" ")

        self.device_code_credential = DeviceCodeCredential(
            client_id, tenant_id=tenant_id
        )
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)


async def get_user_token(self):
    graph_scopes = self.settings["graphUserScopes"]
    access_token = self.device_code_credential.get_token(graph_scopes)
    return access_token.token


async def display_access_token(graph: Graph):
    token = await graph.get_user_token()
    print("User token:", token, "\n")


async def get_user(self):
    # Only request specific properties using $select
    query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        select=["displayName", "mail", "userPrincipalName"]
    )

    request_config = (
        UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
    )

    user = await self.user_client.me.get(request_configuration=request_config)
    return user


async def greet_user(graph: Graph):
    user = await graph.get_user()
    if user:
        print("Hello,", user.display_name)
        # For Work/school accounts, email is in mail property
        # Personal accounts, email is in userPrincipalName
        print("Email:", user.mail or user.user_principal_name, "\n")
