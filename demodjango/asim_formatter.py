import json

import ddtrace
from ddtrace import tracer

from django_log_formatter_asim import ASIMFormatter


class DDASIMFormatter(ASIMFormatter):
    def _datadog_trace_dict(self):

        # source: https://docs.datadoghq.com/tracing/other_telemetry/connect_logs_and_traces/python/

        event_dict = {}

        span = tracer.current_span()
        trace_id, span_id = (str((1 << 64) - 1 & span.trace_id), span.span_id) if span else (None, None)

        # add ids to structlog event dictionary
        event_dict['dd.trace_id'] = str(trace_id or 0)
        event_dict['dd.span_id'] = str(span_id or 0)

        # add the env, service, and version configured for the tracer
        event_dict['dd.env'] = ddtrace.config.env or ""
        event_dict['dd.service'] = ddtrace.config.service or ""
        event_dict['dd.version'] = ddtrace.config.version or ""

        return event_dict


    def format(self, record):
        log_dict = json.loads(super().format(record))

        log_dict.update(self._datadog_trace_dict())

        return json.dumps(log_dict)
