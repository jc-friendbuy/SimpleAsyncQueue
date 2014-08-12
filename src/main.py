import time
from async_task_queue.Queue import Queue
from async_task_queue.Function import Function

_after_first_checkpoint = False

if __name__ == '__main__':

    print("Starting the queue test.")
    print("Two tasks are created and executed concurrently, then a checkpoint is reached.  Afterwards, the queue is "
          "filled again and re-run, and the final checkpoint is reached.")

    queue = Queue(5)

    def first_callback(the_queue):
        print('First end callback')

    def second_callback(the_queue):
        global _after_first_checkpoint
        print('Second end callback')
        input('First checkpoint reached.  Press return to continue.')
        _after_first_checkpoint = True
        the_queue.add_task(Function(third_task, third_task_callback))
        the_queue.add_callback(third_callback)

    def third_callback(the_queue):
        input('Second checkpoint reached.  Press return to exit.')


    def first_task():
        time.sleep(1)
        print('First task')

    def first_task_finished_callback():
        print('First task done')
        
    def second_task():
        print('Second task')

    def second_task_finished_callback():
        print('Second task done')

    def third_task():
        print('Third task')

    def third_task_callback():
        print('Third task done')

    queue.add_task(Function(first_task, first_task_finished_callback))
    queue.add_task(Function(second_task, second_task_finished_callback))

    queue.add_callback(first_callback)
    queue.add_callback(second_callback)

    queue.start()

    # This sleep is used to let the first queue run finish.  That way, start() will work properly (assuming,
    # of course, the user presses return in the proper amount of time
    while _after_first_checkpoint == False:
        time.sleep(0.1)
    queue.start()
