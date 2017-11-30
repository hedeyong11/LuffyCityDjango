from django.test import TestCase

# Create your tests here.

d={"a":1}

s = d.get("c")

print(type(s))
print(type(1))
if isinstance(True,bool):
    print("ok")