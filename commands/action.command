object_id, action_id = a
obj = Object.get(object_id)
action = Action.get(action_id)
if action in obj.get_actions():
    run_program(con, s, action, self=action, obj=obj)