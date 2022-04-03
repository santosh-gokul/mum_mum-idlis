def resolve_query(command: str, sp_name: str):
    if command == '/start':
        return f"""
Hello there. Welcome to {sp_name}'s bot!

You can order services and make payment seamlessly with me. Here are 
few commands that you can ask me to perform.

1: order: To list down the menu and place order.
2: history: Shows history of purchases made by you.
3: help: To display the commands above, in case you forget'em.

Unfortunately, I don't any other commands as of now!
"""

    if command == 'help':
        return f"""
Hello there. Welcome to {sp_name}'s bot!

You can order services and make payment seamlessly with me. Here are 
few commands that you can ask me to perform.

1: order: To list down the menu and place order.
2: history: Shows history of purchases made by you.
3: help: To display the commands above, in case you forget'em.

Unfortunately, I don't any other commands as of now!
"""
