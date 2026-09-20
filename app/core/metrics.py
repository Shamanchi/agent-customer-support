"""Prometheus metrics for Agent Customer Support."""
from prometheus_client import Counter, Histogram, Gauge, Info

# Application info
app_info = Info("agent_customer_support", "Agent Customer Support application info")
app_info.info({"version": "0.1.0"})

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Business metrics
tickets_created_total = Counter(
    "tickets_created_total",
    "Total tickets created",
    ["source", "language"],
)

tickets_classified_total = Counter(
    "tickets_classified_total",
    "Total tickets classified",
    ["category", "confidence_bucket"],
)

tickets_generated_total = Counter(
    "tickets_generated_total",
    "Total responses generated",
    ["model", "status"],
)

tickets_escalated_total = Counter(
    "tickets_escalated_total",
    "Total tickets escalated",
    ["reason"],
)

classification_confidence = Histogram(
    "classification_confidence",
    "Classification confidence score",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
)

generation_latency_seconds = Histogram(
    "generation_latency_seconds",
    "Response generation latency in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

active_conversations = Gauge(
    "active_conversations",
    "Number of active conversations",
)

rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Total rate limit exceeded events",
    ["endpoint"],
)

llm_errors_total = Counter(
    "llm_errors_total",
    "Total LLM errors",
    ["provider", "model", "error_type"],
)

db_errors_total = Counter(
    "db_errors_total",
    "Total database errors",
    ["operation"],
)