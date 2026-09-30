def build_context(
        resent_messages,
        conversation_summary,
        long_term_memories
):
    context=""
    # 1.conversation summary
    if conversation_summary:
        context+=f"""CONVERSATION SUMMARY:{conversation_summary}"""
    if long_term_memories:
        context+=f"""LONG TERM MEMORIES:
        """
        for memory in long_term_memories:
            context+=(
                f"-{memory['key']}:"
                f"-{memory['value']}\n"
            ) 
    context+=f"""REENT CONVERSATION:
    """        
    for message in resent_messages:
        role=message.type
        content=message.content
        context+=f"{role}:{content}\n"
    return context

