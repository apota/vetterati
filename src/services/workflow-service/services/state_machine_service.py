from transitions import Machine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

from models import CandidateWorkflow, WorkflowState
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)

class StateMachineService:
    """Service for managing workflow state transitions"""
    
    def __init__(self):
        self.workflow_service = WorkflowService()
        
        # Define default workflow states
        self.default_states = [
            'applied',
            'screening',
            'phone_interview',
            'technical_interview',
            'final_interview',
            'reference_check',
            'offer_extended',
            'offer_accepted',
            'hired',
            'rejected',
            'withdrawn'
        ]
        
        # Define valid transitions
        self.default_transitions = [
            {'trigger': 'screen', 'source': 'applied', 'dest': 'screening'},
            {'trigger': 'schedule_phone', 'source': 'screening', 'dest': 'phone_interview'},
            {'trigger': 'pass_phone', 'source': 'phone_interview', 'dest': 'technical_interview'},
            {'trigger': 'pass_technical', 'source': 'technical_interview', 'dest': 'final_interview'},
            {'trigger': 'pass_final', 'source': 'final_interview', 'dest': 'reference_check'},
            {'trigger': 'references_clear', 'source': 'reference_check', 'dest': 'offer_extended'},
            {'trigger': 'accept_offer', 'source': 'offer_extended', 'dest': 'offer_accepted'},
            {'trigger': 'onboard', 'source': 'offer_accepted', 'dest': 'hired'},
            
            # Rejection paths
            {'trigger': 'reject', 'source': ['screening', 'phone_interview', 'technical_interview', 'final_interview', 'reference_check'], 'dest': 'rejected'},
            {'trigger': 'decline_offer', 'source': 'offer_extended', 'dest': 'rejected'},
            
            # Withdrawal paths  
            {'trigger': 'withdraw', 'source': ['applied', 'screening', 'phone_interview', 'technical_interview', 'final_interview'], 'dest': 'withdrawn'},
            
            # Re-evaluation paths
            {'trigger': 'reconsider', 'source': 'rejected', 'dest': 'screening'},
        ]
    
    async def transition_state(
        self, 
        db: AsyncSession,
        workflow_id: str,
        action: str,
        metadata: Dict[str, Any] = None,
        triggered_by: Optional[str] = None
    ) -> bool:
        """Transition workflow to next state based on action"""
        try:
            workflow = await self.workflow_service.get_workflow(db, workflow_id)
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return False
            
            # Get workflow template for custom transitions
            transitions = self.default_transitions
            if workflow.template:
                custom_transitions = workflow.template.transitions
                if custom_transitions:
                    transitions = custom_transitions.get('transitions', self.default_transitions)
            
            # Find valid transition
            current_state = workflow.current_state
            valid_transition = None
            
            for transition in transitions:
                if (transition['trigger'] == action and 
                    (current_state == transition['source'] or 
                     current_state in transition.get('source', []))):
                    valid_transition = transition
                    break
            
            if not valid_transition:
                logger.warning(f"Invalid transition: {action} from {current_state}")
                return False
            
            new_state = valid_transition['dest']
            
            # Record state exit
            await self._record_state_exit(db, workflow, current_state, triggered_by)
            
            # Update workflow state
            workflow.previous_state = current_state
            workflow.current_state = new_state
            
            # Update state history
            if not workflow.state_history:
                workflow.state_history = []
            
            workflow.state_history.append({
                "state": new_state,
                "previous_state": current_state,
                "action": action,
                "entered_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
                "triggered_by": triggered_by
            })
            
            # Update progress percentage
            workflow.progress_percentage = self._calculate_progress(new_state)
            
            # Check if workflow is complete
            if new_state in ['hired', 'rejected', 'withdrawn']:
                workflow.status = 'completed'
                workflow.completed_at = datetime.utcnow()
            
            workflow.updated_at = datetime.utcnow()
            
            # Record state entry
            await self._record_state_entry(db, workflow, new_state, action, metadata, triggered_by)
            
            await db.commit()
            
            logger.info(f"Transitioned workflow {workflow_id} from {current_state} to {new_state} via {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error transitioning workflow state: {e}")
            await db.rollback()
            return False
    
    async def get_valid_actions(
        self, 
        db: AsyncSession,
        workflow_id: str
    ) -> List[Dict[str, Any]]:
        """Get valid actions for current workflow state"""
        try:
            workflow = await self.workflow_service.get_workflow(db, workflow_id)
            if not workflow:
                return []
            
            current_state = workflow.current_state
            
            # Get workflow template for custom transitions
            transitions = self.default_transitions
            if workflow.template:
                custom_transitions = workflow.template.transitions
                if custom_transitions:
                    transitions = custom_transitions.get('transitions', self.default_transitions)
            
            valid_actions = []
            for transition in transitions:
                if (current_state == transition['source'] or 
                    current_state in transition.get('source', [])):
                    valid_actions.append({
                        'action': transition['trigger'],
                        'destination_state': transition['dest'],
                        'description': transition.get('description', ''),
                        'requires_approval': transition.get('requires_approval', False)
                    })
            
            return valid_actions
            
        except Exception as e:
            logger.error(f"Error getting valid actions: {e}")
            return []
    
    async def _record_state_exit(
        self, 
        db: AsyncSession,
        workflow: CandidateWorkflow,
        state_name: str,
        triggered_by: Optional[str]
    ):
        """Record when a workflow exits a state"""
        # Find the current state record
        current_state_record = await db.execute(
            select(WorkflowState).where(
                WorkflowState.workflow_id == workflow.id,
                WorkflowState.state_name == state_name,
                WorkflowState.exited_at.is_(None)
            ).order_by(WorkflowState.entered_at.desc())
        )
        
        state_record = current_state_record.scalar_one_or_none()
        if state_record:
            state_record.exited_at = datetime.utcnow()
            state_record.duration_minutes = int(
                (state_record.exited_at - state_record.entered_at).total_seconds() / 60
            )
            state_record.updated_at = datetime.utcnow()
    
    async def _record_state_entry(
        self, 
        db: AsyncSession,
        workflow: CandidateWorkflow,
        state_name: str,
        action: str,
        metadata: Dict[str, Any],
        triggered_by: Optional[str]
    ):
        """Record when a workflow enters a state"""
        state_record = WorkflowState(
            workflow_id=workflow.id,
            state_name=state_name,
            state_data=metadata or {},
            actions_taken=[action],
            triggered_by=uuid.UUID(triggered_by) if triggered_by else None
        )
        
        db.add(state_record)
    
    def _calculate_progress(self, current_state: str) -> float:
        """Calculate workflow progress percentage based on current state"""
        state_progress = {
            'applied': 10.0,
            'screening': 20.0,
            'phone_interview': 35.0,
            'technical_interview': 50.0,
            'final_interview': 70.0,
            'reference_check': 85.0,
            'offer_extended': 95.0,
            'offer_accepted': 99.0,
            'hired': 100.0,
            'rejected': 100.0,
            'withdrawn': 100.0
        }
        
        return state_progress.get(current_state, 0.0)
    
    async def get_workflow_timeline(
        self, 
        db: AsyncSession,
        workflow_id: str
    ) -> List[Dict[str, Any]]:
        """Get complete timeline of workflow state changes"""
        try:
            result = await db.execute(
                select(WorkflowState)
                .where(WorkflowState.workflow_id == uuid.UUID(workflow_id))
                .order_by(WorkflowState.entered_at)
            )
            
            states = result.scalars().all()
            
            timeline = []
            for state in states:
                timeline.append({
                    'state_name': state.state_name,
                    'entered_at': state.entered_at.isoformat() if state.entered_at else None,
                    'exited_at': state.exited_at.isoformat() if state.exited_at else None,
                    'duration_minutes': state.duration_minutes,
                    'actions_taken': state.actions_taken or [],
                    'state_data': state.state_data or {},
                    'triggered_by': str(state.triggered_by) if state.triggered_by else None,
                    'notes': state.notes
                })
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting workflow timeline: {e}")
            return []
