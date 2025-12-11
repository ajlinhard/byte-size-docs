# SQL Alchemy Relationships
**Yes, absolutely!** The reverse relationship is already set up via `back_populates`.

Looking at the SQLAlchemy model:

```72:73:src/flow_objs/workflow_models.py
    # Relationships
    workflow_question = relationship("WorkflowQuestion", back_populates="tasks")
```

## How It Works

```python
# From Task → Question (reverse navigation)
task = session.query(WorkflowQuestionTask).filter_by(workflow_question_task_id=456).first()

# Access the parent question
question = task.workflow_question
print(question.workflow_question_id)
print(question.dbq_questions_id)

# You can even go further up to the workflow
workflow = task.workflow_question.workflow
print(workflow.workflow_name)
```

## The Bidirectional Chain

| From | To | Attribute |
|------|-----|-----------|
| `Workflow` → | `WorkflowQuestion` | `.questions` |
| `WorkflowQuestion` → | `Workflow` | `.workflow` |
| `WorkflowQuestion` → | `WorkflowQuestionTask` | `.tasks` |
| `WorkflowQuestionTask` → | `WorkflowQuestion` | `.workflow_question` |
| `WorkflowQuestionTask` → | `WorkflowQuestionTaskEvidence` | `.evidence_anchors` |
| `WorkflowQuestionTaskEvidence` → | `WorkflowQuestionTask` | `.task` |
| `WorkflowQuestionTask` → | `WorkflowAIPrompt` | `.prompt` |

## One Caveat with Pydantic Schemas

The **Pydantic schemas don't include the reverse relationships** to avoid circular references:

```python
class WorkflowQuestionTaskSchema(WorkflowQuestionTaskBase):
    evidence_anchors: List['WorkflowQuestionTaskEvidenceSchema'] = Field(default_factory=list)
    prompt: Optional['WorkflowAIPromptSchema'] = None
    # Note: no `workflow_question` field here
```

If you need reverse navigation in Pydantic, you'd need to either:
1. Add the field manually (being careful about circular refs)
2. Use the SQLAlchemy ORM objects directly for navigation
3. Store the `workflow_question_id` (which is already there in the base schema) and query separately

---
# Associated Schema
```python
"""
SQLAlchemy models for workflow-related tables.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, 
    ForeignKey, TIMESTAMP, BigInteger, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Workflow(Base):
    """SQLAlchemy model for workflows table"""
    __tablename__ = 'workflows'
    
    workflow_id = Column(Integer, primary_key=True)
    dbq_id = Column(Integer)
    contention_id = Column(Integer)
    workflow_version = Column(String(50))
    workflow_name = Column(String(200))
    workflow_description = Column(Text)
    workflow_json = Column(JSONB)
    active_fl = Column(Boolean, default=True)
    
    # Relationships
    questions = relationship("WorkflowQuestion", back_populates="workflow", lazy="selectin")


class WorkflowQuestion(Base):
    """SQLAlchemy model for workflow_questions table"""
    __tablename__ = 'workflow_questions'
    
    workflow_question_id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey('workflows.workflow_id'))
    dbq_questions_id = Column(Integer)
    contention_id = Column(Integer)
    dbq_likelihood_percentage = Column(Numeric(5, 2))
    dbq_question_required_fl = Column(Boolean)
    override_response_type = Column(String(100))
    workflow_question_json = Column(JSONB)
    active_fl = Column(Boolean, default=True)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="questions")
    tasks = relationship("WorkflowQuestionTask", back_populates="workflow_question", lazy="selectin")


class WorkflowQuestionTask(Base):
    """SQLAlchemy model for workflow_questions_tasks table"""
    __tablename__ = 'workflow_questions_tasks'
    
    workflow_question_task_id = Column(Integer, primary_key=True)
    workflow_question_id = Column(Integer, ForeignKey('workflow_questions.workflow_question_id'))
    contention_id = Column(Integer)
    contention_sub_flow_id = Column(Integer)
    task_name = Column(String(200))
    task_description = Column(Text)
    task_type = Column(String(100))
    task_json = Column(JSONB)
    task_prompt_id = Column(Integer, ForeignKey('workflow_ai_prompt.prompt_id'))
    task_retain_context_fl = Column(Boolean)
    active_fl = Column(Boolean, default=True)
    insert_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    insert_by = Column(String(100), default='SYSTEM')
    update_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    update_by = Column(String(100), default='SYSTEM')
    
    # Relationships
    workflow_question = relationship("WorkflowQuestion", back_populates="tasks")
    evidence_anchors = relationship("WorkflowQuestionTaskEvidence", back_populates="task", lazy="selectin")
    prompt = relationship("WorkflowAIPrompt", back_populates="tasks")


class WorkflowQuestionTaskEvidence(Base):
    """SQLAlchemy model for workflow_question_tasks_evidence table"""
    __tablename__ = 'workflow_question_tasks_evidence'
    
    workflow_question_tasks_evidence_id = Column(Integer, primary_key=True)
    workflow_question_task_id = Column(Integer, ForeignKey('workflow_questions_tasks.workflow_question_task_id'))
    anchor_type = Column(String(50))
    anchor_details = Column(Text)
    anchor_doc_id = Column(Integer)
    anchor_page_number = Column(Integer)
    anchor_section = Column(String(200))
    anchor_line_phrase = Column(Text)
    anchor_params = Column(JSONB)
    active_fl = Column(Boolean, default=True)
    insert_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    insert_by = Column(String(100), default='SYSTEM')
    update_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    update_by = Column(String(100), default='SYSTEM')
    
    # Relationships
    task = relationship("WorkflowQuestionTask", back_populates="evidence_anchors")


class WorkflowAIPrompt(Base):
    """SQLAlchemy model for workflow_ai_prompt table"""
    __tablename__ = 'workflow_ai_prompt'
    
    prompt_id = Column(Integer, primary_key=True)
    prompt_version = Column(String(50))
    prompt_order = Column(Integer)
    prompt_text = Column(Text)
    prompt_system_msg = Column(Text)
    prompt_instructions = Column(Text)
    prompt_examples = Column(Text)
    model_id = Column(Integer, ForeignKey('workflow_ai_prompt_model.model_id'))
    response_type = Column(String(100))
    insert_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    insert_by = Column(String(100), default='SYSTEM')
    update_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    update_by = Column(String(100), default='SYSTEM')
    
    # Relationships
    model = relationship("WorkflowAIPromptModel", back_populates="prompts")
    tasks = relationship("WorkflowQuestionTask", back_populates="prompt")


class WorkflowAIPromptModel(Base):
    """SQLAlchemy model for workflow_ai_prompt_model table"""
    __tablename__ = 'workflow_ai_prompt_model'
    
    model_id = Column(Integer, primary_key=True)
    model_name = Column(String(200))
    model_description = Column(Text)
    model_type = Column(String(100))
    model_endpoint = Column(String(500))
    insert_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    insert_by = Column(String(100), default='SYSTEM')
    update_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    update_by = Column(String(100), default='SYSTEM')
    
    # Relationships
    prompts = relationship("WorkflowAIPrompt", back_populates="model")


class FormAnswersLog(Base):
    """SQLAlchemy model for form_answers_log table"""
    __tablename__ = 'form_answers_log'
    
    form_answer_log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    claim_output_file_log_id = Column(BigInteger, nullable=False)
    workflow_question_id = Column(Integer, ForeignKey('workflow_questions.workflow_question_id'), nullable=False)
    dbq_questions_id = Column(Integer, nullable=False)
    answer_value = Column(Text)
    answer_data_type = Column(Text)
    answer_type = Column(Text)
    answer_json = Column(JSONB)
    answer_change_reason = Column(Text)
    answer_stage = Column(Text)
    insert_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    insert_by = Column(Text, default='SYSTEM')
    update_dt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.now)
    update_by = Column(Text, default='SYSTEM')

```

## Pydantic Validation Method
```python
"""
Pydantic v2 schemas for workflow-related tables.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from decimal import Decimal


# ============= Workflow Schemas =============

class WorkflowBase(BaseModel):
    """Base schema for workflow"""
    workflow_id: int
    dbq_id: Optional[int] = None
    contention_id: Optional[int] = None
    workflow_version: Optional[str] = Field(None, max_length=50, description="YYYY.MM.DD.BUILD")
    workflow_name: Optional[str] = Field(None, max_length=200)
    workflow_description: Optional[str] = None
    workflow_json: Dict[str, Any] = Field(default_factory=dict)
    active_fl: bool = True
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('workflow_json', mode='before')
    @classmethod
    def parse_workflow_json(cls, v):
        """Handle JSON string or dict from database"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v if v is not None else {}


class WorkflowSchema(WorkflowBase):
    """Schema for workflow with relationships"""
    questions: List['WorkflowQuestionSchema'] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# ============= Workflow Question Schemas =============

class WorkflowQuestionBase(BaseModel):
    """Base schema for workflow question"""
    workflow_question_id: int
    workflow_id: int
    dbq_questions_id: int
    contention_id: Optional[int] = None
    dbq_likelihood_percentage: Optional[Decimal] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Likelihood percentage (0-100)"
    )
    dbq_question_required_fl: Optional[bool] = None
    override_response_type: Optional[str] = Field(None, max_length=100)
    workflow_question_json: Dict[str, Any] = Field(default_factory=dict)
    active_fl: bool = True
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('workflow_question_json', mode='before')
    @classmethod
    def parse_workflow_question_json(cls, v):
        """Handle JSON string or dict from database"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v if v is not None else {}

    @property
    def effective_response_type(self) -> Optional[str]:
        """Get the effective response type (override if present, else from DBQ)"""
        if self.override_response_type:
            return self.override_response_type
        if self.dbq_question:
            return self.dbq_question.response_type.value
        return None
    
    @property
    def is_bot_answerable(self) -> bool:
        """Check if question can be answered by bot"""
        if not self.dbq_question:
            return False
        return self.dbq_question.response_type in [
            ResponseType.BOT, 
            ResponseType.BOT_APPROVAL
        ]
    
    @property
    def requires_human_review(self) -> bool:
        """Check if human review is needed"""
        if not self.dbq_question:
            return True
        return self.dbq_question.response_type in [
            ResponseType.HUMAN,
            ResponseType.HUMAN_SUPPORT,
            ResponseType.BOT_APPROVAL
        ]


class WorkflowQuestionSchema(WorkflowQuestionBase):
    """Schema for workflow question with relationships"""
    tasks: List['WorkflowQuestionTaskSchema'] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# ============= Workflow Question Task Schemas =============

TaskType = Literal[
    "Search", "choice", "Free Text", "Retrieval", 
    "Field Extraction", "Agentic", "Classification"
]


class WorkflowQuestionTaskBase(BaseModel):
    """Base schema for workflow question task"""
    workflow_question_task_id: int
    workflow_question_id: int
    contention_id: Optional[int] = None
    contention_sub_flow_id: Optional[int] = None
    task_name: Optional[str] = Field(None, max_length=200)
    task_description: Optional[str] = None
    task_type: Optional[str] = Field(None, max_length=100)
    task_json: Dict[str, Any] = Field(default_factory=dict)
    task_prompt_id: Optional[int] = None
    task_retain_context_fl: Optional[bool] = None
    active_fl: bool = True
    insert_dt: Optional[datetime] = None
    insert_by: Optional[str] = None
    update_dt: Optional[datetime] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('task_json', mode='before')
    @classmethod
    def parse_task_json(cls, v):
        """Handle JSON string or dict from database"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v if v is not None else {}


class WorkflowQuestionTaskSchema(WorkflowQuestionTaskBase):
    """Schema for workflow question task with relationships"""
    evidence_anchors: List['WorkflowQuestionTaskEvidenceSchema'] = Field(default_factory=list)
    prompt: Optional['WorkflowAIPromptSchema'] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============= Workflow Question Task Evidence Schemas =============

AnchorType = Literal["document", "page", "form field", "word/phrase", "NLP"]


class WorkflowQuestionTaskEvidenceBase(BaseModel):
    """Base schema for workflow question task evidence"""
    workflow_question_tasks_evidence_id: int
    workflow_question_task_id: int
    anchor_type: Optional[str] = Field(None, max_length=50)
    anchor_details: Optional[str] = None
    anchor_doc_id: Optional[int] = None
    anchor_page_number: Optional[int] = None
    anchor_section: Optional[str] = Field(None, max_length=200)
    anchor_line_phrase: Optional[str] = None
    anchor_params: Dict[str, Any] = Field(default_factory=dict)
    active_fl: bool = True
    insert_dt: Optional[datetime] = None
    insert_by: Optional[str] = None
    update_dt: Optional[datetime] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('anchor_params', mode='before')
    @classmethod
    def parse_anchor_params(cls, v):
        """Handle JSON string or dict from database"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v if v is not None else {}


class WorkflowQuestionTaskEvidenceSchema(WorkflowQuestionTaskEvidenceBase):
    """Schema for workflow question task evidence"""
    model_config = ConfigDict(from_attributes=True)


# ============= Workflow AI Prompt Schemas =============

ResponseType = Literal["Answer", "supporting", "choice", "json", "documents"]


class WorkflowAIPromptBase(BaseModel):
    """Base schema for workflow AI prompt"""
    prompt_id: int
    prompt_version: Optional[str] = Field(None, max_length=50)
    prompt_order: Optional[int] = None
    prompt_text: Optional[str] = None
    prompt_system_msg: Optional[str] = None
    prompt_instructions: Optional[str] = None
    prompt_examples: Optional[str] = None
    model_id: Optional[int] = None
    response_type: Optional[str] = Field(None, max_length=100)
    insert_dt: Optional[datetime] = None
    insert_by: Optional[str] = None
    update_dt: Optional[datetime] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowAIPromptSchema(WorkflowAIPromptBase):
    """Schema for workflow AI prompt with relationships"""
    model: Optional['WorkflowAIPromptModelSchema'] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============= Workflow AI Prompt Model Schemas =============

class WorkflowAIPromptModelBase(BaseModel):
    """Base schema for workflow AI prompt model"""
    model_id: int
    model_name: Optional[str] = Field(None, max_length=200)
    model_description: Optional[str] = None
    model_type: Optional[str] = Field(None, max_length=100)
    model_endpoint: Optional[str] = Field(None, max_length=500)
    insert_dt: Optional[datetime] = None
    insert_by: Optional[str] = None
    update_dt: Optional[datetime] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowAIPromptModelSchema(WorkflowAIPromptModelBase):
    """Schema for workflow AI prompt model"""
    model_config = ConfigDict(from_attributes=True)


# ============= Form Answers Log Schemas =============

class FormAnswersLogBase(BaseModel):
    """Base schema for form answers log"""
    form_answer_log_id: int
    claim_output_file_log_id: int
    workflow_question_id: int
    dbq_questions_id: int
    answer_value: Optional[str] = None
    answer_data_type: Optional[str] = None
    answer_type: Optional[str] = None
    answer_json: Dict[str, Any] = Field(default_factory=dict)
    answer_change_reason: Optional[str] = None
    answer_stage: Optional[str] = None
    insert_dt: Optional[datetime] = None
    insert_by: Optional[str] = None
    update_dt: Optional[datetime] = None
    update_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('answer_json', mode='before')
    @classmethod
    def parse_answer_json(cls, v):
        """Handle JSON string or dict from database"""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v if v is not None else {}


class FormAnswersLogSchema(FormAnswersLogBase):
    """Schema for form answers log"""
    model_config = ConfigDict(from_attributes=True)


# ============= Task Execution Result Schemas =============

class TaskExecutionResult(BaseModel):
    """Schema for task execution result"""
    task_id: int
    task_name: str
    task_type: str
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    evidence_found: List[Dict[str, Any]] = Field(default_factory=list)
    context_to_retain: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class QuestionExecutionResult(BaseModel):
    """Schema for question execution result"""
    workflow_question_id: int
    dbq_questions_id: int
    question_required: bool
    question_likelihood: Optional[Decimal] = None
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    tasks_results: List[TaskExecutionResult] = Field(default_factory=list)
    final_answer: Optional[str] = None
    confidence_score: Optional[float] = None
    execution_time_ms: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionResult(BaseModel):
    """Schema for complete workflow execution result"""
    workflow_id: int
    workflow_name: str
    execution_start_time: datetime
    execution_end_time: Optional[datetime] = None
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    questions_results: List[QuestionExecutionResult] = Field(default_factory=list)
    total_questions: int = 0
    completed_questions: int = 0
    failed_questions: int = 0
    total_execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)

```
