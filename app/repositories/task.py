from models.deal import AgentTask
from repositories.base import BaseRepository
from schemas.v1.agent_task import AgentTaskPydantic


class TaskRepository(BaseRepository):
    def create_task_for_deal(self, agent_task: AgentTask):
        self.session.add(agent_task)
        self.session.commit()
        return agent_task.task_id


    def get_task_by_id(self, task_id: int) -> AgentTaskPydantic:
        # Query the database for the AgentTask with the given task_id
        task = self.session.query(AgentTask).filter(AgentTask.task_id == task_id).first()

        # Convert the SQLAlchemy model instance to a Pydantic model instance
        if task:
            return AgentTaskPydantic.model_validate(task)
        else:
            return None  # Or raise an exception if you prefer
