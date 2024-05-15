from instorage.services.output_parsing.boolean_guard_output_parser import (
    BooleanGuardOutputParser,
)
from instorage.services.output_parsing.output_parser import (
    ListOutputParser,
    PydanticOutputParser,
    TextOutputParser,
)
from instorage.services.service import ServiceInDBWithUser


class OutputParserFactory:
    @classmethod
    def create(cls, service: ServiceInDBWithUser):
        match service.output_format:
            case "json":
                return PydanticOutputParser(schema=service.json_schema)

            case "list":
                return ListOutputParser()

            case "boolean":
                return BooleanGuardOutputParser()

            case _:
                return TextOutputParser()
