from contextvars import ContextVar

client_ip_var: ContextVar[str] = ContextVar("client_ip", default="unknown")
