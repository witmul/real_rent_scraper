# from time import sleep
#
# temp = 0
# total = 1000
#
# for n in range(1000):
#     temp += 1
#     print('\r' + '[Progress]:[%s%s]%.2f%%;' % (
#     '█' * int(temp*20/total), ' ' * (20-int(temp*20/total)),
#     float(temp/total*100)), end='')
#     sleep(0.01)


from time import sleep
from tqdm import tqdm

for i in tqdm(range(1000)):
    sleep(0.01)