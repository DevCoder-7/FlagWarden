def configure_telemetry(app) -> None:
    """Enable optional OpenTelemetry tracing when the otel extra is installed."""
    from .config import get_settings

    if not get_settings().otel_enabled:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError as exc:
        raise RuntimeError("OTEL_ENABLED=true requires installation with the [otel] extra") from exc

    provider = TracerProvider(resource=Resource.create({"service.name": "flagwarden"}))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
