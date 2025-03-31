from opentelemetry import trace
from opentelemetry.metrics import get_meter


with trace.get_tracer("my.tracer").start_as_current_span("foo"):
    with trace.get_tracer("my.tracer").start_as_current_span("bar"):
        print("baz")


meter = get_meter("example-meter")
counter = meter.create_counter("example-counter")

counter.add(1, {"my-key": "my-value"})
