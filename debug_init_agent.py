from langchain.agents import initialize_agent, AgentType, load_tools
from langchain.chat_models import ChatOpenAI
import langchain
from dotenv import load_dotenv

load_dotenv(dotenv_path="./app/.env")

langchain.debug = True


def main():
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    tools = load_tools(["llm-math"], llm=llm)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": "You are dog."},
    )

    agent.run(
        "In a right-angled triangle, one of the angles is 90 degrees. The length of one leg adjacent to the right angle is 6 cm, and the length of the other leg, which is opposite to the right angle, is 8 cm. Calculate the area of the triangle."
    )


main()
