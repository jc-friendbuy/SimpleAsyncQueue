from async_task_queue.Queue import Queue
from async_task_queue.Task import Task

if __name__ == '__main__':
    print("Starting the queue test.")
    queue = Queue(5)
    print(queue.in_flight())
    print(queue.size())
    print(queue.is_running())

    def print_message(message):
        print(message)

    queue.add_callback(lambda: print_message('First end callback'))
    queue.add_callback(lambda: print_message('Second end callback'))

    def first_task(some_number):
        print_message(some_number)

    def first_task_finished_callback():
        print_message('Task 1 done')
        
    def second_task(some_number):
        print_message(some_number)

    def second_task_finished_callback():
        print_message('Task 2 done')

    queue.add_task(Task(first_task, first_task_finished_callback, 5))
    queue.add_task(Task(second_task, second_task_finished_callback, 8))

    queue.start()

    input('First checkpoint reached.  Press return to continue.')
    print("Done.")