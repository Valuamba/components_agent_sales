from openai import OpenAI
import openai
import os


def create_completion(messages, temperature, output = True, model: str = 'gpt-4', **kwargs):    
    client = openai.OpenAI()

    response = client.chat.completions.create(model=model, messages=messages, temperature=temperature, stream=True, **kwargs)
    collected_messages = []
    for chunk in response:
        if chunk.choices[0].delta.content:
            if output:
                print(chunk.choices[0].delta.content, end='')
            collected_messages.append(chunk.choices[0].delta.content)

    return ''.join(collected_messages)
    