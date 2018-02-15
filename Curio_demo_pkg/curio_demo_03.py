"""
curio_demo_3.py - Curio tutorial.

(from https://curio.readthedocs.io/en/latest/tutorial.html)

We added a kid task into the mix - now add monitoring.

(Using the monitor, we can kill the kid sleep task before the 1000 second
limit is reached.  However, we get an ugly traceback.)
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
    The kid has his/her own task.

    Note - also using the curio sleep timer instead of standard.

    :return:
    """
    print('Building the Millennium Falcon in Minecraft')
    await curio.sleep(1000)


async def parent():
    """
    The parent is (somewhat) patiently waiting for the kid.

    3. Add the curio monitoring framework.

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

"""
3. Add the curio monitoring framework.
"""
if __name__ == '__main__':
    curio.run(parent, with_monitor=True)
    
# EOF

# Added the ability to monitor the curio tasks externally.
