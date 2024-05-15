from typing import Optional

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from instorage.database.tables.assistant_table import Assistants
from instorage.database.tables.base_class import Base, BasePublic
from instorage.database.tables.service_table import Services
from instorage.database.tables.users_table import Users


class Workflows(BasePublic):
    name: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey(Users.id, ondelete="CASCADE"))

    steps: Mapped[list["Steps"]] = relationship(order_by="Steps.order")


class Filters(BasePublic):
    type: Mapped[str] = mapped_column()
    chain_breaker_message: Mapped[str] = mapped_column()


class Steps(BasePublic):
    order: Mapped[Optional[int]] = mapped_column()
    workflow_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(Workflows.id, ondelete="CASCADE")
    )
    assistant_id: Mapped[int] = mapped_column(ForeignKey(Services.id))
    filter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(Filters.id, ondelete="CASCADE")
    )

    filter: Mapped[Filters] = relationship()
    service: Mapped[Services] = relationship()


assistants_steps_guardrails_table = Table(
    "assistants_steps_guardrails",
    Base.metadata,
    Column(
        "assistant_id", ForeignKey(Assistants.id, ondelete="CASCADE"), primary_key=True
    ),
    Column("step_id", ForeignKey(Steps.id, ondelete="CASCADE"), primary_key=True),
)
