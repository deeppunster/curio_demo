"""
curio_demo_2.py - Curio tutorial.

(from https://curio.readthedocs.io/en/latest/tutorial.html)

Let’s add a few more tasks into the mix, e.g. the kid task.

(This edition hangs until the kid task finishes.)
"""

import curio


async def countdown(n):
    """
    A simple countdown timer based on the curio sleep rather than standard.

    :param n: number of seconds to sleep
    :return:
    """
    while n > 0:
        print('T-minus', n)
        await curio.sleep(1)
        n -= 1


async def kid():
    """
    2. The kid has his/her own task.

    Note - also using the curio sleep timer instead of standard.

    :return:
    """
    print('Building the Millennium Falcon in Minecraft')
    await curio.sleep(1000)


async def parent():
    """
    The parent is (somewhat) patiently waiting for the kid.

    :return:
    """
    kid_task = await curio.spawn(kid)
    await curio.sleep(5)

    print("Let's go")
    count_task = await curio.spawn(countdown, 10)
    await count_task.join()

    print("We're leaving!")
    await kid_task.join()
    print('Leaving')

if __name__ == '__main__':
    curio.run(parent)
    
# EOF

# Added a task that causes the parent task to hang until the child task
# finishes.
