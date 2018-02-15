"""
curio_demo_1.py - Curio tutorial.

(from https://curio.readthedocs.io/en/latest/tutorial.html)

Here is a simple curio hello world program – a task that prints a simple
countdown as you wait for your kid to put her shoes on.

(Note - tested with Python 3.6)
"""

import curio


async def countdown(n):
    """
    1. A simple countdown timer based on the curio sleep rather than standard.

    :param n: number of seconds to sleep
    :return:
    """
    while n > 0:
        print('T-minus', n)
        await curio.sleep(1)
        n -= 1

if __name__ == '__main__':
    curio.run(countdown, 10)

# EOF

# Using a curio-based countdown timer.
