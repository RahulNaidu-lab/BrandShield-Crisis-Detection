import uuid
import time
from typing import Dict, Any

class Planner:
    """Planner orchestrates monitoring plans based on user config and evaluator feedback."""

    def __init__(self, policy_store=None):
        self.policy_store = policy_store or {}

    def create_plan(self, user_config: Dict[str, Any], baseline_summary: Dict[str, Any]=None, feedback: Dict[str, Any]=None) -> Dict[str, Any]:
        plan_id = str(uuid.uuid4())
        cadence = user_config.get('cadence', 60)
        sensitivity = user_config.get('sensitivity', 0.8)
        sample_size = user_config.get('sample_size', 200)

        if feedback and feedback.get('adjustment'):
            adj = feedback['adjustment']
            cadence = max(10, cadence + adj.get('cadence_delta', 0))
            sample_size = max(10, sample_size + adj.get('sample_delta', 0))

        plan = {
            'plan_id': plan_id,
            'keyword': user_config.get('keyword'),
            'since': user_config.get('since'),
            'limit': sample_size,
            'cadence': cadence,
            'sensitivity': sensitivity,
            'filters': user_config.get('filters', {})
        }
        return plan

    def adjust_policy(self, decision: Dict[str, Any]):
        if 'suggested_action' in decision:
            self.policy_store.update(decision['suggested_action'])
        return self.policy_store
