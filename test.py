import uuid
name = '123'

# print(uuid.uuid3(uuid.NAMESPACE_DNS, name))
# a = uuid.uuid3(uuid.NAMESPACE_DNS, name)
# print(len(str(a)))

print(str(uuid.uuid3(uuid.NAMESPACE_DNS, 'etaac')) == '6ae19394-c3f4-3b83-9775-708f60a7548b')




# a = []
#
# print(type(a))