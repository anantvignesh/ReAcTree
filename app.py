import chainlit as cl

from basic_work_flow import sample_workflow_bot

@cl.on_chat_start
async def on_chat_start():
    bot = sample_workflow_bot()

    # Input
    state = {"input": "hello world"}
    
    # Thread
    thread = {"configurable": {"thread_id": "1"}}

    # Run the graph until the first interruption
    for event in bot.graph.stream(state, thread, stream_mode="values"):
        print(event)
    
    cl.user_session.set("bot", bot)
    cl.user_session.set("thread", thread)
    cl.user_session.set("state", state)


@cl.on_message
async def on_message(message: cl.Message):
    bot = cl.user_session.get("bot")
    thread = cl.user_session.get("thread")
    state = cl.user_session.get("state")

    msg = cl.Message(content=message.content)
    await msg.send()
    
    # async for chunk in runnable.astream(
    #     {"question": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # ):
    #     await msg.stream_token(chunk)

    # We now update the state as if we are the human_feedback node
    bot.graph.update_state(thread, {"user_feedback": message.content}, as_node="human_feedback")

    # Continue the graph execution
    for event in bot.graph.stream(None, thread, stream_mode="values"):
        print(event)