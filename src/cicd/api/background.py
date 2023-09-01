import sys
from datetime import datetime

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.cli import main
from dramatiq.rate_limits import ConcurrentRateLimiter
from dramatiq.rate_limits.backends import RedisBackend
from dramatiq.results import Results
from gevent import monkey

monkey.patch_all()  # noqa

result_backend = RedisBackend()
broker = RabbitmqBroker()
broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(broker)


backend = RedisBackend()
MUTEX = ConcurrentRateLimiter(backend, "distributed-mutex", limit=2)


@dramatiq.actor
def one_at_a_time():
    with MUTEX.acquire(raise_on_failure=False) as acquired:
        if acquired:
            print("Lock was acquired.")


rabbitmq_broker = RabbitmqBroker(host="rabbitmq")
dramatiq.set_broker(rabbitmq_broker)


@dramatiq.actor
def print_current_date():
    print(datetime.now())


if __name__ == "__main__":
    sys.exit(main())
