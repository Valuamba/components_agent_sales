from models.deal import AgentTask
from repositories.base import BaseRepository


class TaskRepository(BaseRepository):
    def create_task_for_deal(self, agent_task: AgentTask):
        with self.session_scope() as session:
            session.add(agent_task)
            session.commit()
            return agent_task.task_id
