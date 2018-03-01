"""
CurioQueue.py - play with Curio queues.

This edition uses a curio queue to pass the words to the spell checker.
"""

import os
# import logging
from enum import Enum
from logging.config import dictConfig
from logging import basicConfig, getLogger
from logging import debug, info
import yaml  # from PyYAML library

from curio import run, spawn, TaskGroup, sleep, Queue
from curio.debug import schedtrace
from functools import reduce
from operator import mul

from CurioQueuePkg.HunSpellChecker import HunSpellCheckerClass

__author__ = 'Travis Risner'
__project__ = "PlayCurio"
__creation_date__ = "02/02/2018"
# "${CopyRight.py}"

log = None

node_name = 'localhost'


class CurioQueueStatus(Enum):
    """
    Enumeration used to manage each of the RabbitMQ queues.
    """
    QUEUE_CLOSED = 'closed'
    QUEUE_OPEN = 'open'
    QUEUE_ERROR = 'error'


class CurioQueueProducerClass:
    """
    Provide a class to submit an entry to a curio queue and hide all the
    details.
    """

    def __init__(self, curio_queue: Queue):
        """
        Provide placeholders for the the producer.
        """
        self.queue = curio_queue
        self.status = CurioQueueStatus.QUEUE_CLOSED
        return

    async def producer_start(self):
        """
        Open queue for messages.

        :return:
        """
        if self.status != CurioQueueStatus.QUEUE_OPEN:
            self.status = CurioQueueStatus.QUEUE_OPEN
        return

    async def send_message(self, msg: str):
        """
        Insert a message into the queue.

        :param msg: word to add to queue
        :return:
        """
        msg_to_send = msg
        if self.status == CurioQueueStatus.QUEUE_OPEN:
            try:
                await self.queue.put(msg)
            except RuntimeError as xcp:
                debug(f'Unable to send message: {msg_to_send}', exc_info=xcp)
                raise
        return

    async def producer_stop(self):
        """
        Close queue after discarding any remaining values.

        :return:
        """
        await self.queue.join()
        self.status = CurioQueueStatus.QUEUE_CLOSED
        return


class CurioQueueConsumerClass:
    """
    Provide a class to retrieve an entry from a curio queue and hide
    all the details.
    """

    def __init__(self, curio_queue: Queue):
        """
        Provide placeholders for the the producer.
        """
        self.queue = curio_queue
        self.status = CurioQueueStatus.QUEUE_CLOSED
        return

    async def consumer_start(self):
        """
        Open queue for messages.

        :return:
        """
        if self.status != CurioQueueStatus.QUEUE_OPEN:
            self.status = CurioQueueStatus.QUEUE_OPEN
        return

    async def get_message(self) -> str:
        """
        Retrieve a message from the queue.

        :return: the message received or None
        """
        msg_received = None
        if self.status == CurioQueueStatus.QUEUE_OPEN:
            try:
                msg_received = await self.queue.get()
            except RuntimeError as xcp:
                debug(f'Unable to retrieve message.', exc_info=xcp)
                raise
        return msg_received

    async def consumer_stop(self):
        """
        Close queue after discarding any remaining values.

        :return:
        """
        await self.queue.task_done()
        self.status = CurioQueueStatus.QUEUE_CLOSED
        return


class PlayCurioClass:
    """
    PlayCurioClass - play with Curio library.
    """

    def __init__(self):
        self.factor = 10
        debug('PlayCurioClass init started')
        self.spell_checker = HunSpellCheckerClass()
        self.all_word_queue = Queue()
        self.good_word_queue = Queue()
        self.stop_word = '!!!STOP!!!'
        self.raw_word_list = ('good', 'baad', 'ugly', 'gross', 'albatross',
                              'easparate', 'gem', 'clock', 'quantum',
                              'bathymetry', 'silly')
        return

    async def fib(self, nbr: int) -> int:
        """
        Compute Fibonacci numbers (brute force)

        :param nbr: Fibonacci number to compute
        :return: desired Fibonacci number
        """
        result = reduce(mul, range(1, nbr + 1), 1)
        debug(f'fib for {nbr} is {result}')
        return result

    async def fib_runner(self, nbr: int):
        """
        Run recursive fib until final number derived as a means of spacing
        out the submission of words and to chew up some CPU time.

        :param nbr:
        :return:
        """
        print(f'fib_runner started with {nbr} x {self.factor}')
        adjusted_nbr = nbr * self.factor
        fib_task = await spawn(self.fib, adjusted_nbr)
        result = await fib_task.join()
        word_to_check = self.raw_word_list[nbr]
        debug(f'word extracted: {word_to_check}')
        cqp = CurioQueueProducerClass(curio_queue=self.all_word_queue)
        await cqp.producer_start()
        await cqp.send_message(word_to_check)
        await cqp.producer_stop()
        print(f'Fibrunner finished with {result}')
        return

    async def word_check(self):
        """
        Extract words from the all_word_queue and check the spelling.  If
        passed by the spell checker, add to the good_word_queue, else print
        to standard out.

        :return:
        """
        debug('Got to word_check')
        cqc = CurioQueueConsumerClass(curio_queue=self.all_word_queue)
        await cqc.consumer_start()
        cqp = CurioQueueProducerClass(curio_queue=self.good_word_queue)
        await cqp.producer_start()
        async for word in self.all_word_queue:
            debug(f'word_check received {word}')
            if word == self.stop_word:
                break
            if self.spell_checker.check_word(word):
                await self.good_word_queue.put(word)
            else:
                print(f'{word} rejected by Hunspell')
        await cqc.consumer_stop()
        await cqp.producer_stop()
        debug('word_check ending')
        return

    async def run_curio(self):
        """
        Start running tasks asynchronously.

        :return:
        """
        debug('run_curio processes beginning')

        # start spell checker task
        async with TaskGroup() as check_task:
            debug('Starting TaskGroup check_task')
            await check_task.spawn(self.word_check())
            async with TaskGroup() as word_tasks:
                debug('Starting TaskGroup word_tasks')
                for task_nbr in range(10, 0, -1):
                    debug(f'dispatching word_task: {task_nbr}')
                    await word_tasks.spawn(self.fib_runner(task_nbr))
                await word_tasks.join()
                # await sleep(1)
                debug('All tasks in word_tasks finished')
                cqp = CurioQueueProducerClass(curio_queue=self.all_word_queue)
                await cqp.producer_start()
                await cqp.send_message(self.stop_word)
                await cqp.producer_stop()
                # await self.all_word_queue.put(self.stop_word)
            await sleep(1)
            await check_task.join()
            cqp = CurioQueueProducerClass(curio_queue=self.good_word_queue)
            await cqp.producer_start()
            await cqp.send_message(self.stop_word)
            await cqp.producer_stop()
            # await self.good_word_queue.put(self.stop_word)
            debug('All tasks in check_task finished')

        # print out the good words
        print(f'\nGood words found:')
        cqc = CurioQueueConsumerClass(curio_queue=self.good_word_queue)
        await cqc.consumer_start()
        while True:
            word = await cqc.get_message()
            # async for word in self.good_word_queue:
            if word == self.stop_word:
                break
            print(f'\t{word}')
        await cqc.consumer_stop()
        debug('run_curio processes ending')
        return


class MainClass:
    """
    Main class to start things rolling.
    """

    def __init__(self):
        """
        Get things started.
        """
        self.play_curio = None
        return

    def run_play_curio(self):
        """
        Run the play async class for testing.

        :return:
        """
        debug('run_play_curio started')
        self.play_curio = PlayCurioClass()
        debug('Starting up curio')
        run(self.play_curio.run_curio, with_monitor=True,
            debug=schedtrace)
        debug('curio finished')
        return

    @staticmethod
    def start_logging(work_dir: str, debug_name: str):
        """
        Establish the logging for all the other scripts.

        :param work_dir:
        :param debug_name:
        :return: (nothing)
        """

        # Set flag that no logging has been established
        logging_started = False

        # find our working directory and possible logging input file
        _workdir = work_dir
        _logfilename = debug_name

        # obtain the full path to the log information
        _debugConfig = os.path.join(_workdir, _logfilename)

        # verify that the file exists before trying to open it
        if os.path.exists(_debugConfig):
            try:
                #  get the logging params from yaml file and instantiate a log
                with open(_logfilename, 'r') as _logdictfd:
                    _logdict = yaml.load(_logdictfd)
                dictConfig(_logdict)
                logging_started = True
            except Exception as xcp:
                print('The file {} exists, but does not contain appropriate '
                      'logging directives.'.format(_debugConfig))
                raise ValueError('Invalid logging directives.')
        else:
            print('Logging directives file {} either not specified or not '
                  'found'.format(_debugConfig))

        if not logging_started:
            # set up minimal logging
            _logfilename = 'debuginfo.txt'
            _debugConfig = os.path.join(_workdir, _logfilename)
            basicConfig(filename=_logfilename, level=info, filemode='w')
            print('Minimal logging established to '
                  '{}'.format(_debugConfig))

        # start logging
        global log
        log = getLogger(__name__)
        info('Logging started: working directory is {}'.format(_workdir))
        return

    async def test_curio_queue(self):
        """
        Test that the curio processes are working.

        :return:
        """
        test_queue = Queue()
        cqp = CurioQueueProducerClass(curio_queue=test_queue)
        await cqp.producer_start()
        await cqp.send_message(msg='Tasting, Tasting 123 Tasting')
        await cqp.producer_stop()
        cqc = CurioQueueConsumerClass(curio_queue=test_queue)
        await cqc.consumer_start()
        msg = await cqc.get_message()
        debug(f'Test message was: {msg}')
        await cqc.consumer_stop()
        return


if __name__ == "__main__":
    workdir = os.getcwd()
    debug_file_name = 'debug_info.yaml'
    run_main = MainClass()
    run_main.start_logging(workdir, debug_file_name)
    print('Starting curio queue test...')
    run(run_main.test_curio_queue)
    print('Curio queue test completed successfully')
    run_main.run_play_curio()
    debug('Do it again')
    run_main.run_play_curio()

# EOF
