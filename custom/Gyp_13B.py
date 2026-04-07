def execute_command(cmd, obj):
    if isinstance(obj, Unsafe):
        obj.execute(cmd)
    else:
        print("safe")

handler = get_handler(flag)
execute_command(cmd, handler)