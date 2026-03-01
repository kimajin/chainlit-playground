import chainlit as cl


@cl.on_chat_start
async def main() -> None:
    await cl.Message(content="Hello World").send()
