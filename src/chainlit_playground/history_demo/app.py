import os
import uuid
from datetime import UTC, datetime

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict


@cl.password_auth_callback
async def auth_callback(username: str, _password: str) -> cl.User | None:
    """A dummy authentication callback.

    This callback only allows "guest@example.com" and any password.
    """
    if username != "guest@example.com":
        return None
    return cl.User(
        identifier="guest", metadata={"role": "guest", "provider": "credentials"}
    )


@cl.data_layer
def data_layer() -> SQLAlchemyDataLayer:
    return SQLAlchemyDataLayer(conninfo=os.environ["CHAINLIT_CONNINFO"])


@cl.on_chat_resume
async def on_chat_resume(_: ThreadDict) -> None:
    pass


@cl.on_chat_start
async def on_chat_start() -> None:
    user = cl.user_session.get("user")
    await cl.Message(content=f"ようこそ {user.identifier} さん").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    now = datetime.now(UTC).isoformat()
    trace_id = str(uuid.uuid4())
    await cl.Message(content=f"Received: {message.content}").send()

    async with cl.Step(name="dummy_step") as step:
        step.input = {"received_message": message.content}
        step.output = {"save_at_utc": now, "trace_id": trace_id}
