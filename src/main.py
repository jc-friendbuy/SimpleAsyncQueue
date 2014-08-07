import time
from async_task_queue.Queue import Queue
from async_task_queue.Function import Function

if __name__ == '__main__':
    print("Starting the queue test.")
    queue = Queue(5)

    def first_callback(the_queue):
        print('First end callback')

    def second_callback(the_queue):
        print('Second end callback')
        input('First checkpoint reached.  Press return to continue.')

        def third_task(callback):
            print('Third task')
            callback()

        def third_task_callback():
            print('Third task done')

        def third_callback(the_queue):
            print('This is finished')
            input('Second checkpoint reached.  Press return to exit.')

        print(queue.is_running())
        print(queue.size())

        queue.add_task(Function(third_task, third_task_callback))
        queue.add_callback(third_callback)
        queue.start()


    queue.add_callback(first_callback)
    queue.add_callback(second_callback)

    def first_task(callback):
        print(queue.in_flight())
        print(1)
        callback()

    def first_task_finished_callback():
        print('Task 1 done')
        
    def second_task(callback):
        print(queue.in_flight())
        print(2)
        callback()

    def second_task_finished_callback():
        print('Task 2 done')

    queue.add_task(Function(first_task, first_task_finished_callback))
    queue.add_task(Function(second_task, second_task_finished_callback))

    queue.start()
    queue.start()
