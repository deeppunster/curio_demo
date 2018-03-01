"""
curio_demo_12.py - Curio tutorial.

(from https://curio.readthedocs.io/en/latest/tutorial.html)

Kid uses Fibonacci numbers for building the Minecraft game, but now runs it
in a separate process.
"""

import curio
import signal

# an event object for tracking permission from the parent
start_evt = curio.Event()


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


async def friend(name):
    """
    Create a friend task to help build the Millennium Falcon.

    :param name: Name of friend
    :return:
    """
    print(f'Hi, my name is {name}')
    print('Playing Minecraft')
    try:
        await curio.sleep(1000)
    except curio.CancelledError:
        print(f'{name} going home')
        raise

def fib(n):
    """
    Compute the n'th Fibonacci number.
    :param n: target Fibonacci number
    :return: the appropriate number
    """
    if n <=2:
        return 1
    else:
        return fib(n-1) + fib(n-2)


async def kid():
    """
    The kid has his/her own task.

    Add the curio monitoring framework.

    The kid captures the cancel request, complains, then accedes.

    The kid invites a few friends over to help.

    The kids wait for permission before starting.

    The kids complain until they can start playing.

    The kid uses Fibonacci numbers in playing Minecraft.

    12. The kid runs the Fibonacci number generator in a separate process.

    Note - also using the curio sleep timer instead of standard.

    :return:
    """
    while True:
        try:
            print('Can I play?')
            await curio.timeout_after(1, start_evt.wait)
            break
        except curio.TaskTimeout:
            print('Wha!?')

    print('Building the Millennium Falcon in Minecraft')

    async with curio.TaskGroup() as f:

        await f.spawn(friend, 'Max')
        await f.spawn(friend, 'Lillian')
        await f.spawn(friend, 'Thomas')
        try:
            total = 0
            for fib_nbr in range(50):
                total += await curio.run_in_process(fib, fib_nbr)
                print(f'Total so far is {total} for {fib_nbr}')
            await curio.sleep(1000)
        except curio.CancelledError as xcp:
            print('Fine. Saving my work.')
            raise


async def parent():
    """
    The parent is (somewhat) patiently waiting for the kid.

    The parent cancels the kid task after waiting 10 seconds.

    The parent makes the kids wait five seconds before allowing them to
    start playing.

    Provide for emergency stopping of tasks.

    :return:
    """
    goodbye = curio.SignalEvent(signal.SIGINT, signal.SIGTERM)

    kid_task = await curio.spawn(kid)
    await curio.sleep(5)

    print('Yes, go play.')
    await start_evt.set()
    # await curio.sleep(5)

    await goodbye.wait()
    del goodbye

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

# Kid is now running the CPU intensive task in a separate process (thread).
