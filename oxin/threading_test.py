# from multiprocessing import Process, current_process
# import time
# import os

# def spawn(num):
#     print('------------------------------------------------')
#     name = current_process().name
#     print(name, 'Starting')
#     print(num)
#     print('parent process id:', os.getppid())
#     print('process id:', os.getpid())
#     print(name, 'Exiting')
#     print('------------------------------------------------')
#     time.sleep(1)


# class Worker(Process):
#     def run(self):
#         print('------------------------------------------------')
#         name = current_process().name
#         print(name, 'Starting')
#         print('parent process id:', os.getppid())
#         print('process id:', os.getpid())
#         print(name, 'Exiting')
#         print('------------------------------------------------')
#         time.sleep(1)


# if __name__ == '__main__':
#     # for i in range(5):
#     #     p = Process(name='process-%s' %(i), target=spawn, args=(i,))
#     #     p.start()
#     #     p.join() # this line allows you to wait for processes, withous this, the processes dont run in order

#     #     print(f'Process p is alive: {p.is_alive()}')

#     for i in range(5):
#         p = Worker(name='process-%s' %(i))
#         p.start()
#         p.join() # this line allows you to wait for processes, withous this, the processes dont run in order

#         print(f'Process p is alive: {p.is_alive()}')




# import time
# from timeit import default_timer as timer
# from multiprocessing import Pool, cpu_count


# def square(n):

#     time.sleep(2)

#     return n * n


# def main():

#     start = timer()

#     print(f'starting computations on {cpu_count()} cores')

#     values = (2, 4, 6, 8)

#     with Pool() as pool:
#         res = pool.map(square, values)
#         print(res)

#     end = timer()
#     print(f'elapsed time: {end - start}')

# if __name__ == '__main__':
#     main()





# import time
# from timeit import default_timer as timer
# from multiprocessing import Pool, cpu_count


# def power(x, n):

#     time.sleep(1)

#     return x ** n


# def main():

#     start = timer()

#     print(f'starting computations on {cpu_count()} cores')

#     values = ((2, 2), (4, 3), (5, 5))

#     with Pool() as pool:
#         res = pool.starmap(power, values)
#         print(res)

#     end = timer()
#     print(f'elapsed time: {end - start}')


# if __name__ == '__main__':
#     main()



# from multiprocessing import Pool
# import functools


# def inc(x):
#     return x + 1

# def dec(x):
#     return x - 1

# def add(x, y):
#     return x + y

# def smap(f):
#     return f()


# def main():

#     f_inc = functools.partial(inc, 4)
#     f_dec = functools.partial(dec, 2)
#     f_add = functools.partial(add, 3, 4)

#     with Pool() as pool:
#         res = pool.map(smap, [f_inc, f_dec, f_add])

#         print(res)


# if __name__ == '__main__':
#     main()



# from decimal import Decimal, getcontext
# from timeit import default_timer as timer

# def pi(precision):

#     getcontext().prec = precision

#     return sum(1/Decimal(16)**k *
#         (Decimal(4)/(8*k+1) -
#          Decimal(2)/(8*k+4) -
#          Decimal(1)/(8*k+5) -
#          Decimal(1)/(8*k+6)) for k in range (precision))


# start = timer()
# values = (4000, 5000, 6000)
# data = list(map(pi, values))
# #print(data)

# end = timer()
# print(f'sequentially: {end - start}')



# from decimal import Decimal, getcontext
# from timeit import default_timer as timer
# from multiprocessing import Pool, current_process
# import time


# def pi(precision):

#     getcontext().prec=precision

#     return sum(1/Decimal(16)**k *
#         (Decimal(4)/(8*k+1) -
#          Decimal(2)/(8*k+4) -
#          Decimal(1)/(8*k+5) -
#          Decimal(1)/(8*k+6)) for k in range (precision))

# def main():

#     start = timer()

#     with Pool(3) as pool:

#         values = (4000, 5000, 6000)
#         data = pool.map(pi, values)
#         #print(data)

#     end = timer()
#     print(f'paralelly: {end - start}')


# if __name__ == '__main__':
#     main()



# from random import random
# from math import sqrt
# from timeit import default_timer as timer


# def pi(n):

#     count = 0

#     for i in range(n):

#         x, y = random(), random()

#         r = sqrt(pow(x, 2) + pow(y, 2))

#         if r < 1:
#             count += 1

#     return 4 * count / n


# start = timer()
# pi_est = pi(100000000)
# end = timer()

# print(f'elapsed time: {end - start}')
# print(f'π estimate: {pi_est}')



import random
from multiprocessing import Pool, cpu_count
from math import sqrt
from timeit import default_timer as timer


def pi_part(n):
    #print(n)

    count = 0

    for i in range(int(n)):

        x, y = random.random(), random.random()

        r = sqrt(pow(x, 2) + pow(y, 2))

        if r < 1:
            count += 1

    return count


def main():

    start = timer()

    np = cpu_count()
    print(f'You have {np} cores')

    n = 100000000

    part_count = [n/np for i in range(np)]

    with Pool(processes=np) as pool:

        count = pool.map(pi_part, part_count)
        pi_est = sum(count) / (n * 1.0) * 4

        end = timer()

        print(f'elapsed time: {end - start}')
        print(f'π estimate: {pi_est}')

if __name__=='__main__':
    main()