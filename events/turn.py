def generate_wml(data):
    turn_num = data.get("turn_number", "1")
    return f"""[event]
    name=turn {turn_num}
[/event]"""
