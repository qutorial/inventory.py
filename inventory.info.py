#!/usr/bin/env python3

import os
import sys
import logging
import csv
import argparse

global logger
global parser

parser = argparse.ArgumentParser(description='Script to help inventorize laptops')
parser.add_argument('--verbose', '-v', action='count')
args = parser.parse_args()

def readline(f):
  with open(f, 'r') as f:
    return f.readline().strip()


def getLogger():
  logger = logging.getLogger('inventory_info')
  if args.verbose is None:
    logger.setLevel(logging.ERROR)
  elif args.verbose == 1:
      logger.setLevel(logging.INFO)
  elif args.verbose >= 2:
      logger.setLevel(logging.DEBUG)
  ch = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  return logger

class Nic:
  def __init__(self, name, mac):
    self.name = name
    self.mac = mac

  def __repr__(self):
    return "%s - %s" % (self.name, self.mac)

class PlatformListerLinux:
  def __init__(self, logger):
    if os.geteuid() != 0:
      logger.error("Shall be run as root, %s EUID instead.." % os.geteuid())

  def getAllInterfaces(self):
    # skip loopback and virtuals
    names = [x for x in os.listdir('/sys/class/net/') if x[0:2] not in ['lo', 'vi']]
    nics = []
    for name in names:
      f = "/sys/class/net/" + name + "/address"
      mac = readline(f)
      nics.append(Nic(name, mac))

    return nics

  def getDeviceModel(self):
    model = readline("/sys/devices/virtual/dmi/id/product_family")
    return model

  def getDeviceSerial(self):
    sn = readline("/sys/devices/virtual/dmi/id/chassis_serial")
    return sn



def getPlatformLister(logger):
  if sys.platform == "linux":
    return PlatformListerLinux(logger)
  else:
    logger.error("not support OS for Platform detection")
    return None


def main():
  logger = getLogger()
  logger.info("inventory started")
  platlister = getPlatformLister(logger)
  print(platlister.getAllInterfaces())
  print(platlister.getDeviceModel())
  print(platlister.getDeviceSerial())

if __name__ == "__main__":
  main()

