from models.deal import AgentTask
from repositories.base import BaseRepository


class TaskRepository(BaseRepository):
    def create_task_for_deal(self, agent_task: AgentTask):
        self.session.add(agent_task)
        self.session.commit()
        return agent_task.task_id
