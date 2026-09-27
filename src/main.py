from src.agents.agriculture_agent import create_agent
from src.memory.conversation_memory import get_checkpointer


def main():
    checkpointer = get_checkpointer()

    agent = create_agent(model)

    # application logic


if __name__ == "__main__":
    main()