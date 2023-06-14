import logging
import copy

logger = logging.getLogger(__name__)


class MessageLine:
    STOP: str = "stop"
    LENGHT: str = "length"
    FUNCTION_CALL: str = "function_call"
    CONTENT_FILTER: str = "content_filter"
    role: str = "user"
    content: str = ""
    finish_reason: str | None = None

    def __init__(
        self,
        data: dict[str, dict[str, str] | str] | None = None,
        role: str | None = None,
        content: str | None = None,
    ):
        if data:
            self.set_by_data(data)
        if role:
            self.role = role
        if content:
            self.content = content

    def set_by_data(self, data: dict[str, dict[str, str] | str]):
        delta = data.get("delta", None)
        if not delta:
            delta = dict()
        self.role = delta.get("role", "")
        self.content = delta.get("content", "")
        finish_reason = data.get("finish_reason", None)
        if finish_reason == "null":
            finish_reason = None
        self.finish_reason = finish_reason

    def make_message(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    def __str__(self):
        message = f"role: {self.role}, content: {self.content}"
        if self.finish_reason:
            message += f", finish_reason: {self.finish_reason}"
        return f"< MessageLine-{message} >"

    def __add__(self, other):
        temp = copy.deepcopy(self)
        if other.role:
            temp.role = other.role
        if other.content:
            temp.content = self.content + other.content
        if other.finish_reason:
            temp.finish_reason = other.finish_reason
        return temp


class MessageBox:
    def __init__(self):
        self.messaes: list[MessageLine] = []

    def add_message(self, message: MessageLine):
        self.messaes.append(message)

    def make_messages(self, system_text: str | None = None) -> list[dict[str, str]]:
        messages = []
        if system_text:
            messages = [[MessageLine(role="system", content=system_text)]]
        return messages + [message.make_message() for message in self.messaes]

    def __len__(self):
        return len(self.messaes)

    def __str__(self):
        print(self.messaes)
        return f"< MessageBox-{len(self.messaes)} >"
