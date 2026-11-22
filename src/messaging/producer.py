import asyncio
import json
import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.config.settings import settings

logger = logging.getLogger(__name__)


async def start_producer() -> AIOKafkaProducer | None:
    """Start the Kafka producer. Returns None (app keeps running) if Kafka is off or unreachable."""
    if not settings.kafka_enabled:
        logger.info("Kafka disabled (KAFKA_ENABLED=false).")
        return None

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        acks="all",
        enable_idempotence=True,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )
    try:
        await asyncio.wait_for(producer.start(), timeout=10)
    except Exception as e:
        logger.warning(
            "Kafka unavailable at %s (%s). Uploads will stay 'received'.",
            settings.kafka_bootstrap_servers, e,
        )
        try:
            await producer.stop()
        except Exception:
            pass
        return None

    logger.info("Kafka producer connected to %s", settings.kafka_bootstrap_servers)
    return producer


async def stop_producer(producer: AIOKafkaProducer | None) -> None:
    if producer is not None:
        await producer.stop()


async def publish_message(
    producer: AIOKafkaProducer | None, topic: str, key: str, value: dict
) -> bool:
    """Publish one message. True only if the broker confirmed it."""
    if producer is None:
        return False
    try:
        await producer.send_and_wait(topic, value=value, key=key)
        return True
    except KafkaError as e:
        logger.error("Kafka publish to %s failed for %s: %s", topic, key, e)
        return False


async def publish_document(producer: AIOKafkaProducer | None, message: dict) -> bool:
    """Publish a newly uploaded document to the raw topic, keyed by doc_id."""
    return await publish_message(
        producer, settings.kafka_topic_raw, message["doc_id"], message
    )
