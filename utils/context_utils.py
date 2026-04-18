from contextvars import ContextVar

# 全局上下文存储 trace_id（并发安全，每个请求独立）
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")