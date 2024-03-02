import re

FINAL_ANSWER_ACTION = "Final Answer:"


def parse_action(text: str):
    # Define a constant to simulate the FINAL_ANSWER_ACTION placeholder
    regex = r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"

    includes_answer = FINAL_ANSWER_ACTION in text
    action_match = re.search(regex, text, re.DOTALL)

    if action_match and includes_answer:
        if text.find(FINAL_ANSWER_ACTION) < text.find(action_match.group(0)):
            # if final answer is before the matched text, extract and return the final answer part
            start_index = text.find(FINAL_ANSWER_ACTION) + len(FINAL_ANSWER_ACTION)
            end_index = text.find("\n\n", start_index)
            return {"type": "finish", "output": text[start_index:end_index].strip()}
        else:
            raise Exception("Final answer and parsable action error.")

    if action_match:
        action = action_match.group(1).strip()
        action_input = action_match.group(2).strip()
        # Simplified processing of action_input, removed SQL specific handling
        return {"type": "action", "action": action, "input": action_input}

    elif includes_answer:
        return {"type": "finish", "output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}

    if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
        raise Exception("Could not parse output: Missing action.")
    elif not re.search(r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL):
        raise Exception("Could not parse output: Missing action input.")
    else:
        raise Exception("Could not parse output.")