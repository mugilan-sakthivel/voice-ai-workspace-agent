from pydantic import BaseModel


class IntegrationConnectRequest(BaseModel):
    user_id: str = "demo-user"
    suite: str
    app: str


class IntegrationConnectResponse(BaseModel):
    connection_url: str
    integration_id: str
    expires_at: str


class ConnectedAccount(BaseModel):
    suite: str
    app: str
    status: str
    connected_account_id: str

