from typing import List, Text

from branches.branch import Branch
from branches.completion import GPTCompletionResolver
from branches.utils import get_block_schema_branch_instruction, messaging_history_to_str


class DiscountBranch:
    def __init__(self, branch, branches, gpt_completion_resolver: GPTCompletionResolver):
        self.branch: Branch = branch
        self.branches: List[Branch] = branches
        self.block_schema = get_block_schema_branch_instruction(self.branch, self.branches)
        self.gpt_completion_resolver: GPTCompletionResolver = gpt_completion_resolver

    def name(self) -> Text:
        return "discount"

    def run(self, deal_id: int, messaging_history):
        messaging_history_str = messaging_history_to_str(messaging_history)
        stop = ['\nAction observation:', '\n\tAction observation:', '\nBranch observation:', '\n\tBranch observation:']
        resp = self.gpt_completion_resolver.create_completion(name=self.name(), deal_id=deal_id, messages=[
            {"role": "user", "content": f"""
    You are Client Dialog Sales Manager at company that supply clients with parts or components for manufacturers. Your responsibility is   
    understand the client intents and decide on which direction to move messaging with client to close him need and increase chanse   
    of purchasing.  

    Please read client messaging history at block [CLIENT MESSAGING HISTORY] and use block schema [BLOCK SCHEMA] it would help you to choose  
    right direction. Make decision relatively to latest message, but use oldest messages for richer context.

    [CLIENT MESSAGING HISTORY]  
     {messaging_history_str}
    [/CLIENT MESSAGING HISTORY]  

    [BLOCK SCHEMA]   
    {self.block_schema}

    If


    [/BLOCK SCHEMA]   

    **Use the following format of answer:** 

    Use this format if you are going throw block schema instruction tree:

    Decision Point: the name of decision point, that you thought on
    Condition: the name of condition that you moved on
    Observation: the conclusion about thoughts  
    ... (this Decision Point/Condition/Observation can repeat N times)  

    Use this format if you need to complete action.  

    Action: the action that you are going to do    
    Action observation: the result of action
    ... (this Action/Action observation: can repeat N times) 

    Use this format if you need to move to branch

    Branch: the branch you need move on
    Branch observation: the result of work branch

    Thought: I now know the final answer  
    Conclusion: the final observation about thoughts

    DO NOT USE MARKDOWN FORMAT FOR RESPONSE.
    """}
        ], temperature=0.3, stop=stop)

        return resp
