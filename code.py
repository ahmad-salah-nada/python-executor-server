# should pass
a = 5
for i in range(0, 10000000):
    a += (i * 2) % (i + 5) / 2

print(i)


# should TLE
# a = 5
# for i in range(0, 100000000):
#     a += (i * 2) % (i + 5) / 2
# 
# print(i)