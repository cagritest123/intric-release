import asyncio

from instorage.assistants.assistant import AssistantResponse
from instorage.assistants.assistant_runner import AssistantRunner
from instorage.main.logging import get_logger
from instorage.sessions.session import SessionInDB
from instorage.sessions.session_service import SessionService
from instorage.workflows.steps import Step

logger = get_logger(__name__)


class AssistantGuardRunner:
    def __init__(
        self,
        assistant_runner: AssistantRunner,
        session_service: SessionService,
        guard_step: Step = None,
    ):
        self.assistant_runner = assistant_runner
        self.guard_step = guard_step
        self.session_service = session_service
        self.chain_breaker_message = (
            self.guard_step.filter.chain_breaker_message
            if self.guard_step is not None
            else None
        )

    def _return_chain_breaker_message(self, stream: bool, session: SessionInDB):
        if stream:
            answer = stream_chain_breaker_message(self.chain_breaker_message)
        else:
            answer = self.chain_breaker_message

        return AssistantResponse(answer=answer, info_blobs=[], session=session)

    async def _save_chain_breaker_message_to_session(
        self, input: str, session: SessionInDB = None
    ):
        if session is None:
            # Set session name to the questions
            session = await self.session_service.create_session(
                name=input, assistant=self.assistant_runner.assistant
            )

        await self.session_service.add_question_to_session(
            question=input, answer=self.chain_breaker_message, session=session
        )

        return session

    async def run(self, input: str, stream: bool, session: SessionInDB = None):
        if self.guard_step is not None:
            guard_result = await self.guard_step(input)

            if not guard_result:
                session = await self._save_chain_breaker_message_to_session(
                    input, session=session
                )
                return self._return_chain_breaker_message(stream, session)

            else:
                return await self.assistant_runner.run(
                    question=input,
                    session=session,
                    stream=stream,
                    datastore_result=guard_result.runner_result.datastore_result,
                )
        else:
            return await self.assistant_runner.run(
                question=input, session=session, stream=stream
            )


async def stream_chain_breaker_message(chain_breaker_message):
    for char in chain_breaker_message:
        await asyncio.sleep(0.01)
        yield char
