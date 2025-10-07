import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

def thread_function_1():
    with lock_a:
        with lock_b:
            print("Thread 1 ejecutando")

def thread_function_2():
    with lock_b:
        with lock_a:
            print("Thread 2 ejecutando")

t1 = threading.Thread(target=thread_function_1)
t2 = threading.Thread(target=thread_function_2)

t1.start()
t2.start()
