# -*- coding: utf-8 -*-

from Classes import Child1, Child2
from Service import Service

if __name__ == "__main__":
    service = Service.get_instance()

    child1 = Child1()
    child2 = Child2()

    service.do_something()
