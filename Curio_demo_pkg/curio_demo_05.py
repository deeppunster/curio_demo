"""
curio_demo_5.py - Curio tutorial.

(from https://curio.readthedocs.io/en/latest/tutorial.html)

The kid captures the parent cancellation and raises a stink.
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

    5. The kid captures the cancel request, complains, then accedes.

    Note - also using the curio sleep timer instead of standard.

    :return:
    """
    try:
        print('Building the Millennium Falcon in Minecraft')
        await curio.sleep(1000)
    except curio.CancelledError as xcp:
        print('Fine. Saving my work.')
        raise


async def parent():
    """
    The parent is (somewhat) patiently waiting for the kid.

    The parent cancels the kid task after waiting 10 seconds.

    :return:
    """
    kid_task = await curio.spawn(kid)
    await curio.sleep(5)

    print("Let's go")
    count_task = await curio.spawn(countdown, 10)
    await count_task.join()

    print("We're leaving!")
    try:
        await curio.timeout_after(10, kid_task.join)
    except curio.TaskTimeout:
        print('I warned you!')
        await kid_task.cancel()
    print('Leaving!')

"""
Add the curio monitoring framework.
"""
if __name__ == '__main__':
    curio.run(parent, with_monitor=True)
    
# EOF

# Allow the child task to capture the cancellation and do some cleanup
# before allowing it to proceed.
