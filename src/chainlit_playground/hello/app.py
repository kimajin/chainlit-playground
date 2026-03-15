import chainlit as cl


@cl.on_message
async def main(message: cl.Message) -> None:
    await cl.Message(content=f"Received: {message.content}").send()


@cl.set_starters
async def set_starters(_user: cl.User | None) -> list[cl.Starter]:
    return [
        cl.Starter(
            label="Message",  # 表示されるラベル
            message="Hello World!",  # 送信されるメッセージ
        )
    ]
