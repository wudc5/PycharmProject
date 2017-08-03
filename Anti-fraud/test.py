#coding=utf-8
import os
import json
import commands
from hdfs3 import HDFileSystem


class Dog():
    def __init__(self):
        self.sound = "wang~wang~"
        self.bite = "fsd"
    def bark(self):
        print self.sound


class Husky(Dog):
    def __init__(self):
        Dog.__init__(self)
        self.sound = "ao~ao~ "

niub = Husky()
# niub.sound = "kao kao"
niub.bark()
print niub.__class__
print niub.__dict__
