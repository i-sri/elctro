import time

t0 = time.time()
f = open('out.out', 'a')
f.write("some integers"+"2333344"+"   "+"4444")
f.close
t1 = time.time()

print t1-t0

