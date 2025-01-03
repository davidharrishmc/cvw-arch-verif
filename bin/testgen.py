#!/usr/bin/env python3
##################################
# testgen.py
#
# David_Harris@hmc.edu 27 March 2024
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Generate directed tests for functional coverage
##################################

##################################
# libraries
##################################
from datetime import datetime
from random import randint
from random import seed
from random import getrandbits
import os
import re
import sys

##################################
# functions
##################################

def legalizecompr(r):
  # bring into range 8-15 for compressed instructions with limited
  if hasattr(r, '__getitem__'):
    return [rval % 8 + 8 for rval in r]
  else:
    return r % 8 + 8

def shiftImm(imm, xlen):
  imm = imm % xlen
  return str(imm)

def signedImm12(imm, immOffset = False):
#                          ^~~~~~~~~~~~~~~~~ if the imm is used as an offset, restrict the range to [-2047, 2047]
  pos = imm > 0
  imm = imm % pow(2, 12)
  if (imm & 0x800): # Check if the 12th bit (0x800) is set
    imm = imm - 0x1000 # Convert to negative value
  if immOffset and imm == -2048:
    imm += 1 +  pos * 0x0ffe # change to abs(2047) with the sign of the original
  return str(imm)

def unsignedImm12(imm, immOffset = False):
#                          ^~~~~~~~~~~~~~~~~ if the imm is used as an offset, restrict the range to [-2047, 2047]
  pos = imm > 0
  imm = imm % pow(2, 12)
  if immOffset and imm == -2048:
    imm += 1 +  pos * 0x0ffe # change to abs(2047) with the sign of the original
  return str(imm)

def unsignedImm20(imm):
  imm = imm % pow(2, 20)
  return str(imm)

def unsignedImm5(imm):
  imm = imm % pow(2, 5)
  # zero immediates are prohibited
  if test not in ["c.lw","c.sw","c.ld","c.sd","c.lwsp","c.ldsp","c.flw","c.fsw","c.fld","c.fsd"] + csritype:
    if imm == 0:
      imm = 8
  return str(imm)

def ibtype_unsignedImm(xlen, imm):
  if test == "roriw": xlen = 32
  imm = imm % xlen
  return str(imm)

def SextImm6(imm):
  imm = imm % pow(2, 6)
  if (imm & 0x20):
    #if the 6th bit is high, sign extend it
    imm = imm | 0xfffC0
  if (imm == 0):
    imm = 1
  return str(hex(imm))


def ZextImm6(imm):
  imm = imm % pow(2, 6)
  if test not in ["c.lw","c.sw","c.ld","c.sd","c.lwsp","c.ldsp","c.sdsp","c.swsp","c.flwsp","c.fswsp","c.fsdsp","c.fldsp"]:
    if imm == 0:
      imm = 8
  return str(imm)

def signedImm6(imm):
  imm = imm % pow(2, 6)
  if (imm & 0x20):
    imm = imm - 0x40
  return str(imm)

def unsignedImm10(imm):
  imm = imm % pow(2, 10)
  # zero immediates are prohibited
  if imm == 0:
    imm = 16
  return str(imm)

def unsignedImm8(imm):
  imm = imm % pow(2, 8)
  # zero immediates are prohibited
  if imm == 0:
    imm = 16
  return str(imm)

def unsignedImm2(imm):
  imm = imm % pow(2, 2)
  return str(imm)

def unsignedImm1(imm):
  imm = imm % pow(2, 1)
  return str(imm)

def loadFloatReg(reg, val, xlen, flen):
  # Assumes that x2 is loaded with the base addres to avoid repeated `la` instructions
  lines = "" # f"# Loading value {val} into f{reg}\n"
  if test[-1] == "d" or NaNBox_tests == "D":
    precision = 64
    loadop = "fld"
  elif NaNBox_tests == "S":
    precision = 32
    loadop = "flw"
  elif test[-1] == "h":
    precision = 16
    loadop = "flh"
  else:
    precision = 32
    loadop = "flw"
  # if test[-1] == "h":
  #   precision = 16
  #   loadop = "flh"
  # elif test[-1] == "d":
  #   precision = 64
  #   loadop = "fld"
  # else:
  #   precision = 32
  #   loadop = "flw"
  storeop =  "sw" if (min (xlen, flen) == 32) else "sd"
  # loadop  = "flw" if             (flen == 32) else "fld"
  if (precision > xlen): # precision = 64, xlen = 32
  # lines = lines + "la x2, scratch # base address \n"
    lines = lines + f"li x3, 0x{formatstrFP.format(val)[10:18]} # load x3 with 32 MSBs {formatstrFP.format(val)}\n"
    lines = lines + f"li x4, 0x{formatstrFP.format(val)[2:10]} # load x4 with 32 LSBs of {formatstrFP.format(val)}\n"
    lines = lines + f"{storeop} x3, 0(x2) # store x3 (0x{formatstrFP.format(val)[10:18]}) in memory\n"
    lines = lines + f"{storeop} x4, 4(x2) # store x4 (0x{formatstrFP.format(val)[2:10]}) in memory 4 bytes after x3\n"
    lines = lines + f"{loadop} f{reg}, 0(x2) # load {formatstrFP.format(val)} from memory into f{reg}\n"
  else:
  # lines = lines + "la x2, scratch # base address \n"
    lines = lines + f"li x3, {formatstrFP.format(val)} # load x3 with value {formatstrFP.format(val)}\n"
    lines = lines + f"{storeop} x3, 0(x2) # store {formatstrFP.format(val)} in memory\n"
    lines = lines + f"{loadop} f{reg}, 0(x2) # load {formatstrFP.format(val)} from memory into f{reg}\n"
  return lines

def genFrmTests(testInstr):
  lines = ""
  frm = ["dyn", "rdn", "rmm", "rne", "rtz", "rup"]
  csrFrm = ["0x4", "0x3", "0x2", "0x1", "0x0"]
  for roundingMode in frm:
    lines = lines + f"{testInstr}, {roundingMode} # perform operation\n"
  for csrMode in csrFrm:
    lines = lines + f"\n # set fcsr.frm to {csrMode} \n"
    lines = lines + f"fsrmi {csrMode}\n"
    lines = lines + f"{testInstr} # perform operation\n"

  return lines

def writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=None, rs3val=None, frm=False):
  lines = "\n# Testcase " + str(desc) + "\n"
  if (rs1val < 0):
    rs1val = rs1val + 2**xlen
  if (rs2val < 0):
    rs2val = rs2val + 2**xlen
  lines = lines + "li x" + str(rd) + ", " + formatstr.format(rdval) + " # initialize rd to a random value that should get changed\n"
  if (test in rtype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + " # initialize rs2\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", x" + str(rs2) + " # perform operation\n"
  elif (test in i1type):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + " # perform operation\n"
  elif (test in frtype):
    lines = lines + "la x2, scratch\n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    lines = lines + loadFloatReg(rs2, rs2val, xlen, flen)
    if not frm:
      lines = lines + test + " f" + str(rd) + ", f" + str(rs1) + ", f" + str(rs2) + " # perform operation\n"
    else:
      testInstr = f"{test} f{rd}, f{rs1}, f{rs2}"
      lines = lines + genFrmTests(testInstr)
  elif (test in fixtype):
    lines = lines + "la x2, scratch\n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    lines = lines + test + " x" + str(rd) + ", f" + str(rs1) +  " # perform operation\n"
  elif (test in fitype):
    lines = lines + "fsflagsi 0b00000 # clear all fflags\n"
    lines = lines + "la x2, scratch\n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    lines = lines + test + " f" + str(rd) + ", f" + str(rs1) +  " # perform operation\n"
    if not frm:
      lines = lines + test + " f" + str(rd) + ", f" + str(rs1) + " # perform operation\n"
    else:
      testInstr = f"{test} f{rd}, f{rs1}"
      lines = lines + genFrmTests(testInstr)
  elif (test in csrtype):
      lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
      lines = lines + f"{test} x{rd}, mscratch, x{rs1} # perform operation\n"
  elif (test in csritype):
      lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
      lines = lines + f"{test} x{rd}, mscratch, {unsignedImm5(immval)} # perform operation\n"
  elif (test in citype):
    if(test == "c.lui" and rd == 2): # rd ==2 is illegal operand
      rd = 9 # change to arbitrary other register
    elif (test == "c.addiw" and rd == 0):
      rd = 1
    if (test == "c.addi16sp"):
      immval = int(signedImm6(immval)) * 16
      if (immval == 0):
        immval = 16
      lines = lines + test + " sp, " + str(immval) + " # perform operation\n"
    elif test in ["c.lwsp","c.ldsp","c.flwsp","c.fldsp"]:
      if (test == "c.lwsp"):
        storeop = "c.swsp"
        mul = 4
      elif (test == "c.flwsp"):
        storeop = "sw"
        mul = 4
      elif (test == "c.fldsp"):
        mul = 8
        if (xlen == 32):
          storeop = "sw"
        else:
          storeop = "sd"
      else:
        storeop = "c.sdsp"
        mul = 8
      while (rd == 0 and (test not in ["c.flwsp","c.fldsp"])):
        rd = randint(1,31)
      while (rs2 == 2):
        rs2 = randint(1,31)
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + "la " + "sp" + ", scratch" + " # base address \n"
      lines = lines + "addi " + "sp" + ", " + "sp" + ", -" + str(int(ZextImm6(immval))*mul) + " # sub immediate from rs1 to counter offset\n"
      lines = lines + storeop + " x" + str(rs2) + ", " + str(int(ZextImm6(immval))*mul) + "(" + "sp" + ")   # store value to put something in memory\n"
      if (test == "c.flwsp" or test == "c.fldsp"):
        lines = lines + test + " f" + str(rd) + ", " + str(int(ZextImm6(immval))*mul) + "(" + "sp" + ") # perform operation\n"
      else:
        lines = lines + test + " x" + str(rd) + ", " + str(int(ZextImm6(immval))*mul) + "(" + "sp" + ") # perform operation\n"
    else:
      if test in ["c.li", "c.addi", "c.addiw"]:    # Add tests with signed Imm in the list
        lines = lines + test + " x" + str(rd) + ", " + signedImm6(immval) + " # perform operation\n"
      elif test == "c.lui":
        lines = lines + test + " x" + str(rd) + ", " + SextImm6(immval) + " # perform operation\n"
      else:
        lines = lines + test + " x" + str(rd) + ", " + ZextImm6(immval) + " # perform operation\n"
  elif (test in c_shiftitype):
    if (test == "c.srli" or test == "c.srai"):
        rd = legalizecompr(rd)
    if shiftImm(int(ZextImm6(immval)),xlen) == "0":    # imm = 0 isn't allowed
      imm = "1"
    else:
      imm = shiftImm(int(ZextImm6(immval)),xlen)
    lines = lines + "li x" + str(rd) + ", " + formatstr.format(rs2val)+"\n"
    lines = lines + test + " x" + str(rd) + ", " + imm + " # perform operation\n"
  elif (test in crtype):
    if (test in ["c.add", "c.mv"]):
      if (rs2 == 0):
        rs2 = 11
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + "\n"
      lines = lines + test + " x" + str(rd) + ", x" + str(rs2) + " # perform operation\n"
    elif test in ["c.jalr", "c.jr"]:
      if (rs1 == 0):
        rs1 = randint(1, 31)
      if (test == "c.jalr"):
        lines = lines + "li x1" + ", " + formatstr.format(rdval) + " # initialize legalized rd (x1) to a random value that should get changed\n"
      lines = lines + "la x" + str(rs1) + ", 1f\n"
      lines = lines + test + " x" + str(rs1) + " # perform operation\n"
      lines = lines + "nop\nnop\n"
      lines = lines + "1:\n"
  elif (test in catype):
    rd_c = legalizecompr(rd)
    rs2_c = legalizecompr(rs2)
    lines = lines + "li x" + str(rd_c) + ", " + formatstr.format(rs1val) + " # initialize leagalized rd to a random value that should get changed\n"
    lines = lines + "li x" + str(rs2_c) + ", " + formatstr.format(rs2val) + " # initialize rs2\n"
    lines = lines + test + " x" + str(rd_c) +", x" + str(rs2_c) + " # perform operation\n"
  elif (test in cbptype):
    rd = legalizecompr(rd)
    lines = lines + "li x" + str(rd) + ", " + formatstr.format(rdval)+"\n"
    lines = lines + test + " x" + str(rd) + ", " + signedImm6(immval) + " # perform operation\n"
  elif (test in cbtype):
    rs1 = legalizecompr(rs1)
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rs1) + ", some_label_for_cbtype_" + str(immval) + " # perform operation \n"
    lines = lines + "addi x0, x1, 1\n"
    lines = lines + "some_label_for_cbtype_" + str(immval) + ":\n"
    lines = lines + "addi x0, x2, 2\n"
    lines = lines + "nop\nnop\n"
  elif (test in ciwtype): # addi4spn
    rd = legalizecompr(rd)
    lines = lines + "li sp, " + formatstr.format(rs1val) + " # initialize some value to sp \n"
    lines = lines + test + " x" + str(rd) + ", sp, " + str(int(unsignedImm8(immval))*4) + " # perform operation\n"
  elif (test in shiftitype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + shiftImm(immval, xlen) + " # perform operation\n"
  elif (test in shiftiwtype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + shiftImm(immval, 32) + " # perform operation\n"
  elif (test in itype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + signedImm12(immval) + " # perform operation\n"
  elif (test in ibtype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + ibtype_unsignedImm(xlen, immval) + " # perform operation\n"
  elif (test in ibwtype):
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + ibtype_unsignedImm(xlen, immval) + " # perform operation\n"
  elif (test in loaditype):#["lb", "lh", "lw", "ld", "lbu", "lhu", "lwu"]
    if (rs1 != 0):
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
      if (immval == -2048):
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 2047 # increment rs1 by 2047 \n" # ***
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 1 # increment rs1 to bump it by a total of 2048 to compensate for -2048\n"
      else:
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval) + " # sub immediate from rs1 to counter offset\n"
      if (xlen == 32):
        storeop = "sw"
      else:
        storeop = "sd"
      lines = lines + storeop + " x" + str(rs2) + ", " + signedImm12(immval) +" (x" + str(rs1) + ") # store value to put something in memory\n"
      lines = lines + test + " x" + str(rd) + ", " + signedImm12(immval) + "(x" + str(rs1) + ") # perform operation\n"
#      lines = lines + test + " x" + str(rd) + ", 0(x" + str(rs1) + ") # perform operation\n"
  elif (test in cltype):
    rd = legalizecompr(rd)
    rs1 = legalizecompr(rs1)
    rs2 = legalizecompr(rs2)
    while (rs1 == rs2):
      rs2 = randint(8,15)
    if test in ["c.lw","c.ld"]:
      if (test == "c.lw"):
          storeop = "c.sw"
          mul = 4
      else:
          storeop = "c.sd"
          mul = 8
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", -" + str(int(unsignedImm5(immval))*mul) + " # sub immediate from rs1 to counter offset\n"
      lines = lines + storeop + " x" + str(rs2) + ", " + str(int(unsignedImm5(immval))*mul) +"(x" + str(rs1) + ") # store value to put something in memory\n"
      lines = lines + test + " x" + str(rd) + ", " + str(int(unsignedImm5(immval))*mul) + "(x" + str(rs1) + ") # perform operation\n"
    else:
      lines = lines + "la x"       + str(rs1) + ", scratch" + " # base address \n"
      if (test == "c.flw"):
        storeop = "c.sw"
        mul = 4
        lines = lines + "addi x"     + str(rs1) + ", x" + str(rs1) + ", -" + str(int(unsignedImm5(immval))*mul) + " # sub immediate from rs1 to counter offset\n"
        lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + " # load immediate value into integer register\n"
        lines = lines + "sw x" + str(rs2) + ", " + str(int(unsignedImm5(immval))*mul) + "(x" + str(rs1) + ") # store value to memory\n"
        lines = lines +  test + " f" + str(rd)  + ", " + str(int(unsignedImm5(immval))*mul) + "(x" + str(rs1) + ") # perform operation\n"
      elif (test == "c.fld"):
        storeop =  "sw" if (min (xlen, flen) == 32) else "sd"
        mul = 8
        temp1 = 8
        temp2 = 9
        while (temp1 in [rs1, rs2]):
          temp1 = randint(8,15)
        while (temp2 in [rs1, rs2, temp1]):
          temp2 = randint(8,15)
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " +  str(int(unsignedImm5(immval))*mul) + "\n"
        if (flen > xlen): # flen = 6
          rs2val = (rs2val << 32) | (rs1val)
          lines = lines + f"li x{temp1}, 0x{formatstrFP.format(rs2val)[2:10]} # load x{temp1} with 32 MSBs of {formatstrFP.format(rs2val)}\n"
          lines = lines + f"li x{temp2}, 0x{formatstrFP.format(rs2val)[10:18]} # load x{temp2} with 32 LSBs {formatstrFP.format(rs2val)}\n"
          lines = lines + f"{storeop} x{temp1}, {str(int(unsignedImm5(immval))*mul)}(x{rs1}) # store x{temp1} (0x{formatstrFP.format(rs2val)[2:10]}) in memory\n"
          lines = lines + f"addi x{rs1}, x{rs1}, 4 # move address up by 4\n"
          lines = lines + f"{storeop} x{temp2}, {str(int(unsignedImm5(immval))*mul)}(x{rs1}) # store x{temp2} (0x{formatstrFP.format(rs2val)[10:18]}) after 4 bytes in memory\n"
          lines = lines + f"addi x{rs1}, x{rs1}, -4 # move back to scratch\n"
          lines = lines + f"{test} f{rd}, {str(int(unsignedImm5(immval))*mul)}(x{rs1}) # perform operation\n"
        else:
          lines = lines + f"li x{temp1}, {formatstrFP.format(rs2val)} # load x{temp1} with value {formatstrFP.format(rs2val)}\n"
          lines = lines + f"{storeop} x{temp1}, {str(int(unsignedImm5(immval))*mul)}(x{rs1}) # store {formatstrFP.format(rs2val)} in memory\n"
          lines = lines + f"{test} f{rd}, {str(int(unsignedImm5(immval))*mul)}(x{rs1}) # perform operation\n"

  elif (test in clhtype or test in clbtype):
    rd = legalizecompr(rd)
    rs1 = legalizecompr(rs1)
    rs2 = legalizecompr(rs2)
    while (rs1 == rs2):
      rs2 = randint(8,15)
    if (test in clhtype):
      storeop = "c.sh"
      mul = 2
    else:
      storeop = "c.sb"
      mul = 1
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
    lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
    lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", -" + str(int(unsignedImm1(immval))*mul) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + storeop + " x" + str(rs2) + ", " + str(int(unsignedImm1(immval))*mul) +"(x" + str(rs1) + ") # store value to put something in memory\n"
    lines = lines + test + " x" + str(rd) + ", " + str(int(unsignedImm1(immval))*mul) + "(x" + str(rs1) + ") # perform operation\n"
  elif (test in cstype):
    rs1 = legalizecompr(rs1)
    rs2 = legalizecompr(rs2)
    while (rs1 == rs2):
      rs1 = randint(8,15)
    mul = 4 if (test in ["c.sw", "c.fsw"]) else 8
    lines = lines + "la x" + str(rs1) + ", scratch" + " # base address\n"
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2 with random value\n"
    if (test in ["c.fsw", "c.fsd"]):
      if ((test == "c.fsd") and (flen > xlen)):
        temp = 8
        while (temp in [rs1, rs2]):
          temp = randint(8,15)
        lines = lines + "li x" + str(temp) +", " + formatstr.format(rs1val) + " # initialize x" + str(temp) + " with random value{formatstr.format(rs1val)}\n"
        lines = lines + "sw x" + str(rs2) + ", 0(x" + str(rs1) + ")" + " # store " + hex(rs2val) + " in memory\n"
        lines = lines + "sw x" + str(temp) + ", 4(x" + str(rs1) + ")" + " # store " + hex(rs1val) + " in memory\n"
        lines = lines + "fld f" + str(rs2) + ", 0(x" + str(rs1) + ")" + " # load " + hex(rs1val) + hex(rs2val)[2:] + " from memory into fs2\n"
        lines = lines + "sw x0, 0(x" + str(rs1) + ")" + " # clearing the random value store at scratch\n"
        lines = lines + "sw x0, 4(x" + str(rs1) + ")" + " # clearing the random value store at 4(scratch)\n"
      else:
        size = "w" if test == "c.fsw" else "d"
        lines = lines + "s" + size + " x" + str(rs2) + ", 0(x" + str(rs1) + ")" + " # store " + hex(rs2val) + " in memory\n"
        lines = lines + "fl" + size + " f" + str(rs2) + ", 0(x" + str(rs1) + ")" + " # load " + hex(rs2val) + " from memory into fs2\n"
        lines = lines + "s" + size + " x0, 0(x" + str(rs1) + ")" + " # clearing the random value store at scratch\n"
    lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", -" + str(int(unsignedImm5(immval))*mul) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + test + (" f" if test in ["c.fsw","c.fsd"] else " x") + str(rs2) + ", " + str(int(unsignedImm5(immval))*mul) + "(x" + str(rs1) + ") # perform operation \n"

  elif (test in cutype):
    rd = legalizecompr(rd)
    rs1 = legalizecompr(rs1)
    if (test == "c.not"):
      lines = lines + "li x" + str(rd) + ", " + formatstr.format(rs1val)  + " # initialize rd to specific value\n"
      lines = lines + test + " x" + str(rd) + "  # performing not operation on rd and storing it in same register \n"
    elif test in ["c.zext.b","c.zext.h","c.zext.w","c.sext.b","c.sext.h"]:
      lines = lines + "li x" + str(rd) + ", " + formatstr.format(rs1val) + " # initialize leagalized rd to a random value that should get changed\n"
      lines = lines + test + " x" + str(rd) + " # perform operation\n"
  elif (test in stype):#["sb", "sh", "sw", "sd"]
    if (rs1 != 0):
      if (rs2 == rs1): # make sure registers are different so they don't conflict
          rs2 = (rs1 + 1) % 32
          if (rs2 == 0):
            rs2 = 1
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
      if (immval == -2048): # Can't addi 2048 because it is out of range of 12 bit two's complement number
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 2047 # increment rs1 by 2047 \n"
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 1 # increment rs1 to bump it by a total of 2048 to compensate for -2048\n"
      else:
        lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval) + " # sub immediate from rs1 to counter offset\n"
      lines = lines + test + " x" + str(rs2) + ", " + signedImm12(immval) + "(x" + str(rs1) + ") # perform operation \n"
  elif (test in csstype):
    if (test == "c.swsp" or test == "c.fswsp"):
      mul = 4
    elif (test == "c.sdsp" or test == "c.fsdsp"):
      mul = 8
    if (test == "c.fswsp" or test == "c.fsdsp"):
      mv = "fmv.d.x" if (xlen == 64) else "fmv.w.x"
      lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + mv + " f" + str(rs2) + ", x" + str(rs1) + " #put a randomm value into fs2\n"
      lines = lines + "la sp" + ", scratch" + " # base address \n"
      lines = lines + test + " f" + str(rs2) +", " + str(int(ZextImm6(immval))*mul) + "(sp)" + "# perform operation\n"
    else:
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
      lines = lines + "la sp" + ", scratch" + " # base address \n"
      lines = lines + test + " x" + str(rs2) +", " + str(int(ZextImm6(immval))*mul) + "(sp)" + "# perform operation\n"
  elif (test in csbtype):
    rs1 = legalizecompr(rs1)
    rs2 = legalizecompr(rs2)
    while (rs1 == rs2):
      rs2 = randint(8,15)
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
    lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
    lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", -" + unsignedImm2(immval) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + test + " x" + str(rs2) + ", " + unsignedImm2(immval) + "(x" + str(rs1) + ") # perform operation \n"
  elif (test in cshtype):
    rs1 = legalizecompr(rs1)
    rs2 = legalizecompr(rs2)
    while (rs1 == rs2):
      rs2 = randint(8,15)
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val)  + " # initialize rs2\n"
    lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
    lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", -" + str(int(unsignedImm1(immval))*2) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + test + " x" + str(rs2) + ", " + str(int(unsignedImm1(immval))*2) + "(x" + str(rs1) + ") # perform operation \n"
  elif (test in btype):#["beq", "bne", "blt", "bge", "bltu", "bgeu"]
    for same in range(2):
      if (same):
        rs1val = rs2val
        lines = lines + "# same values in both registers\n"
      lines = lines + "nop\n"
      lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
      lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + " # initialize rs2\n"
      lines = lines + test + " x" + str(rs1) + ", x" + str(rs2) + ", some_label_for_btype_" + str(immval) + str(same) + " # perform operation \n"
      lines = lines + "addi x0, x1, 1\n"
      lines = lines + "some_label_for_btype_" + str(immval)+ str(same) + ":\n"
      lines = lines + "addi x0, x2, 2\n"
      lines = lines + "nop\nnop\nnop\nnop\nnop\n"
  elif (test in jtype):#["jal"]
    lines = lines + "jal x" + str(rd) + ", 1f # perform operation\n"
    lines = lines + "nop\n"
    lines = lines + "1:\n"
  elif (test in jalrtype):#["jalr"]
    lines = lines + "la x" + str(rs1) + ", 1f\n"
    lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval, immOffset=True) + " # add immediate to lower part of rs1\n"
    lines = lines + "jalr x" + str(rd) + ", x" + str(rs1) + ", " + signedImm12(immval, immOffset=True) + " # perform operation\n"
    lines = lines + "nop\n"
    lines = lines + "1:\n"
  elif (test in utype):#["lui", "auipc"]
    lines = lines + test + " x" + str(rd) + ", " + unsignedImm20(immval) + " # perform operation\n"
  elif (test in fr4type): #["fmadd.s", "fmsub.s", "fnmadd.s", "fnmsub.s"]
    lines = lines + "la x2, scratch\n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    lines = lines + loadFloatReg(rs2, rs2val, xlen, flen)
    lines = lines + loadFloatReg(rs3, rs3val, xlen, flen)
    if not frm:
      lines = lines + test + " f" + str(rd) + ", f" + str(rs1) + ", f" + str(rs2) + ", f" + str(rs3) + " # perform operation\n"
    else:
      testInstr = f"{test} f{rd}, f{rs1}, f{rs2}, f{rs3}"
      lines = lines + genFrmTests(testInstr)
  elif (test in fltype):#["flw", "flh"]
    while (rs1 == 0):
      rs1 = randint(1, 31)
    while (rs1 == rs2):
      rs2 = randint(1, 31)
    tempreg1 = randint(1,31)
    tempreg2 = randint(1,31)
    while (tempreg1 in [rs1, rs2]):
      tempreg1 = randint(1,31)
    while (tempreg2 in [rs1, rs2, tempreg1]):
      tempreg2 = randint(1,31)
    storeop =  "sw" if (min (xlen, flen) == 32) else "sd"
    lines = lines + "la x" + str(rs1) + ", scratch" + " # base address \n"
    if (immval == -2048): # Can't addi 2048 because it is out of range of 12 bit two's complement number
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 2047 # increment rs1 by 2047 \n"
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 1 # increment rs1 to bump it by a total of 2048 to compensate for -2048\n"
    else:
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval) + " # sub immediate from rs1 to counter offset\n"
    if (flen > xlen): # flen = 64, xlen = 32
      lines = lines + f"li x{tempreg1}, 0x{formatstrFP.format(rs2val)[2:10]} # load x3 with 32 LSBs of {formatstrFP.format(rs2val)}\n"
      lines = lines + f"li x{tempreg2}, 0x{formatstrFP.format(rs2val)[10:18]} # load x3 with 32 MSBs {formatstrFP.format(rs2val)}\n"
      lines = lines + f"{storeop} x{tempreg1}, {signedImm12(immval)}(x{rs1}) # store x3 (0x{formatstrFP.format(rs2val)[2:10]}) in memory\n"
      lines = lines + f"addi x{rs1}, x{rs1}, 4 # move address up by 4\n"
      lines = lines + f"{storeop} x{tempreg2}, {signedImm12(immval)}(x{rs1}) # store x4 (0x{formatstrFP.format(rs2val)[10:18]}) in memory 4 bytes after x3\n"
      lines = lines + f"addi x{rs1}, x{rs1}, - 4 # move back to scratch\n"
    else:
      lines = lines + f"li x{tempreg1}, {formatstrFP.format(rs2val)} # load x3 with value {formatstrFP.format(rs2val)}\n"
      lines = lines + f"{storeop} x{tempreg1}, {signedImm12(immval)}(x{rs1}) # store {formatstrFP.format(rs2val)} in memory\n"
    lines = lines + f"{test} f{rd}, {signedImm12(immval)}(x{rs1}) # perform operation\n"
  elif (test in fstype):#["fsw"]
    while (rs1 == 0):
      rs1 = randint(1, 31)
    lines = lines + f"la x2, scratch # base address\n"
    lines = lines + loadFloatReg(rs2, rs2val, xlen, flen)
    lines = lines + f"la x{rs1}, scratch # base address\n"
    if (immval == -2048): # Can't addi 2048 because it is out of range of 12 bit two's complement number
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 2047 # increment rs1 by 2047 \n"
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 1 # increment rs1 to bump it by a total of 2048 to compensate for -2048\n"
    else:
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + test + " f" + str(rs2)  + ", " + signedImm12(immval) + "(x" + str(rs1) + ") # perform operation\n"
  elif (test in F2Xtype):#["fcvt.w.s", "fcvt.wu.s", "fmv.x.w"]
    while (rs2 == rs1):
      rs2 = randint(1, 31)
    lines = lines + "la x2, scratch" + " # base address \n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    if not frm:
      rm = ", rtz" if (test == "fcvtmod.w.d") else "" # fcvtmod requires explicit rtz rouding mode
      lines = lines + test + " x" + str(rd) + ", f" + str(rs1) + rm + " # perform operation\n"
    else: #                                                       ^~~~~~~~~ adds nothing if test != fcvtmod
      testInstr = f"{test} x{rd}, f{rs1}"
      lines = lines + genFrmTests(testInstr)
  elif (test in fcomptype): # ["feq.s", "flt.s", "fle.s"]
    lines = lines + "la x2, scratch\n"
    lines = lines + loadFloatReg(rs1, rs1val, xlen, flen)
    lines = lines + loadFloatReg(rs2, rs2val, xlen, flen)
    lines = lines + test + " x" + str(rd) + ", f" + str(rs1) + ", f" + str(rs2) + " # perform fcomp-type op\n"
  elif test in X2Ftype: # ["fcvt.s.w", "fcvt.s.wu", "fmv.w.x"]
    lines = lines + "fsflagsi 0b00000\n # clear all fflags\n"
    lines = lines + f"li x{rs1}, {formatstr.format(rs1val)} # load immediate value into integer register\n"
    testInstr = f"{test} f{rd}, x{rs1}"
    if not frm:
      lines = lines + testInstr
    else:
      lines = lines + genFrmTests(testInstr)
  elif test in PX2Ftype: # ["fmvp.d.x"]
    lines = lines + f"li x{rs1}, {formatstr.format(rs1val)} # load immediate value into integer register\n"
    lines = lines + f"li x{rs2}, {formatstr.format(rs2val)} # load immediate value into integer register\n"
    testInstr = f"{test} f{rd}, x{rs1}, x{rs2}"
    if not frm:
      lines = lines + testInstr
    else:
      lines = lines + genFrmTests(testInstr)
  elif test in flitype:
    lines = lines + f"{test} f{rd}, {flivals[rs1]} # perform operation\n"
    #                                      ^~~~~~~~~~~~~~~~~~~~~~~ translate register encoding to C-style literal to make the assembler happy
  elif test in rbtype:
    bs = 0 # TODO: bit select, need to pass it to this function
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + " # initialize rs2\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", x" + str(rs2) + ", " + str(bs) + " # perform operation\n"
  elif test in irtype:
    rnum = 0 # TODO: need to pass it to this function
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs1) + ", " + str(rnum) + " # perform operation\n"
  elif test in lrtype:
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + test + " x" + str(rd) + ", (x" + str(rs1) + ")  # perform operation\n"
  elif test in sctype or test in amotype:
    lines = lines + "li x" + str(rs1) + ", " + formatstr.format(rs1val) + " # initialize rs1\n"
    lines = lines + "li x" + str(rs2) + ", " + formatstr.format(rs2val) + " # initialize rs2\n"
    lines = lines + test + " x" + str(rd) + ", x" + str(rs2) + ", (x" + str(rs1) + ") # perform operation\n"
  else:
    print("Error: %s type not implemented yet" % test)
  f.write(lines)

def writeSingleInstructionSequence(desc, testlist, regconfiglist, rdlist, rs1list, rs2list, rs3list, immvalslist, commentlist, xlen):

    #TODO Hamza: add input prechecks here later

  registerArray = [rdlist, rs1list, rs2list, rs3list]
  global hazardLabel

  lines = ""

  for testindex, test in enumerate(testlist):
    if (test in amotype or test in sctype or test in lrtype or test in rbtype or test in irtype):
      return ""  # TODO: AMO, lr/sc not yet supported; Hamza, please add support
    instype = findInstype('instructions', test, insMap)
    regconfig = regconfiglist[testindex]

    if insMap[instype].get('loadstore') == 'load':
      lines += ( test + " " + regconfig[0] + str(registerArray[0][testindex]) +
        ", " + signedImm12(immvalslist[testindex]) +
        "(" + regconfig[1] + str(registerArray[1][testindex]) + ")" + " # " + commentlist[testindex] + "\n")

    elif insMap[instype].get('loadstore') == 'store':
      lines += (test + " " + regconfig[2] + str(registerArray[2][testindex]) +
        ", " + signedImm12(immvalslist[testindex]) +
        "(" + regconfig[1] + str(registerArray[1][testindex]) + ")" + " # " + commentlist[testindex] + "\n")

    else:
      lines += test
      for regindex, reg in enumerate(regconfiglist[testindex]):
        match reg:
          case 'x' | 'f':
            lines += ","*(lines[-1*len(test):] != test) + " " + reg + str(registerArray[regindex][testindex])
          case 'i':
            if insMap[instype].get('compressed', 0) != 0:
              immval = signedImm6(immvalslist[testindex])
            elif test == "lui" or test == "auipc":
              immval = unsignedImm20(immvalslist[testindex])
            elif instype in ['shiftiwtype', 'ibwtype']:
              immval = shiftImm(immvalslist[testindex], 32)
            elif instype in ['shiftitype', 'ibtype']:
              immval = shiftImm(immvalslist[testindex], xlen)
            elif instype == 'flitype':
              immval = flivals[immvalslist[testindex] % 32]
            else:
              immval = signedImm12(immvalslist[testindex])
            lines += ","*(lines[-1*len(test):] != test) + " " + str(immval)
          case 'l':
            lines += ","*(lines[-1*len(test):] != test) + " " + "arbitraryLabel" + str(hazardLabel) + "\nnop\n"
            lines += "arbitraryLabel" + str(hazardLabel) + ":\nnop\n"
            hazardLabel += 1
      if test == 'fcvtmod.w.d' :
        lines += ", rtz"
      lines += " # " + commentlist[testindex] + "\n"

  return lines

def writeHazardVector(desc, rs1a, rs2a, rda, rs1b, rs2b, rdb, testb, immvala, immvalb, regtotest, rs3a=None, rs3b=None, haz_type='waw', xlen=32):
  # consecutive instructions to trigger hazards

  instype = findInstype('instructions', testb, insMap)
  regconfig = insMap[instype].get('regconfig','xxx_')
  implicitxreg = insMap[instype].get('implicitxreg', '____')
  global hazardLabel

  testa = 'add'

  lines = "\n# Testcase " + str(desc) + "\n"

  match haz_type:
    case 'nohaz':
        pass
    case 'waw' | 'war':
      if regconfig[0] == 'f':
        testa = 'fmul.s'
      elif regconfig[0] == 'x':
        testa = 'add'
    case 'raw':
      if regconfig[regtotest] == 'f':
        testa = 'fmul.s'
      elif regconfig[regtotest] == 'x':
        testa = 'add'
    case _:
      print('invalid hazard type' + haz_type + ' for instruction ' + testb)

  ins2type = findInstype('instructions', testa, insMap)
  regconfig2 = insMap[ins2type].get('regconfig','xxx_')

  if test in jalrtype:
    if haz_type != "raw":
      lines += 'la x' + str(rs1b) + ', arbitraryLabel' + str(hazardLabel) + '\n'
      immvalb = 0
    lines += writeSingleInstructionSequence(desc,
                                [testa],
                                [regconfig2],
                                [rda], [rs1a],
                                [rs2a], [rs3a],
                                [immvala],
                                ["perform first operation"],
                                xlen)
    if haz_type == "raw":
      lines += 'la x' + str(rs1b) + ', arbitraryLabel' + str(hazardLabel) + '\n'
      immvalb = 0
    lines += writeSingleInstructionSequence(desc,
                                [testb],
                                [regconfig],
                                [rdb], [rs1b],
                                [rs2b], [rs3b],
                                [immvalb],
                                ["perform second (triggering) operation"],
                                xlen)
    lines += "arbitraryLabel" + str(hazardLabel) + ":\nnop\n"
    hazardLabel += 1

  else:

    if test in fstype + fltype + stype + loaditype:
      lines += "la " + regconfig[1] + str(rs1b) + ", scratch\n"
      lines += "addi " + 2*(regconfig[1] + str(rs1b) + ", ") + str(signedImm12(-immvalb)) + "\n"
      if haz_type != "war":
        rs1a = rda
        rs2a = 0

    lines += writeSingleInstructionSequence(desc,
                    [testa, testb],
                    [regconfig2, regconfig],
                    [rda, rdb], [rs1a, rs1b],
                    [rs2a, rs2b], [rs3a, rs3b],
                    [immvala, immvalb],
                    ["perform first operation", "perform second (triggering) operation"],
                    xlen)

  f.write(lines)

def findInstype(key, instruction, insMap):
    # within sublists with the key provided, find the first instance of the instruction

    for k, v in insMap.items():
      if hasattr(v, "__getitem__"):
        if instruction in v[key]:
          return k

    print('instruction ' + instruction + ' not found in insMap')
    return 0

def make_unique_hazard(test, regsA, haz_type='nohaz', regchoice=1):
  # set up hazard
  [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
  regsB = [rdb, rs1b, rs2b, rs3b]
  compression = insMap[findInstype('instructions', test, insMap)].get('compressed', 0)

  if compression == 2:
    regsA = legalizecompr(regsA)
    regsB = legalizecompr(regsB)

  match haz_type:
    case "nohaz":
      while (set(regsA) & set(regsB)):
        [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
        regsB = [rdb, rs1b, rs2b, rs3b]
        if compression == 2:
          regsB = legalizecompr(regsB)

    case "waw":
      while (set(regsA[1:]) & set(regsB[1:])):
        [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
        regsB = [rdb, rs1b, rs2b, rs3b]
        if compression == 2:
          regsB = legalizecompr(regsB)
      regsB[0] = regsA[0]

    case "war":
      while (set(regsA) & set(regsB)):
        [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
        regsB = [rdb, rs1b, rs2b, rs3b]
        if compression == 2:
          regsB = legalizecompr(regsB)
      regsB[0] = regsA[regchoice]


    case "raw":
      while (regsB[0] not in regsA):
        [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
        regsB = [rdb, rs1b, rs2b, rs3b]
        if compression == 2:
          regsB = legalizecompr(regsB)
        regsB[regchoice] = regsA[0]

  return regsA, regsB

def randomize(rs1=None, rs2=None, rs3=None, allunique=True):
    if rs1 is None:
      rs1 = randint(1, 31)
    if rs2 is None:
      rs2 = randint(1, 31)
    if (rs3 is not None):
      rs3 = randint(1, 31)
      rs3val = randint(0, 2**xlen-1)
    # all three source registers must be different for corners to work
    while (rs1 == rs2 and allunique):
      rs2 = randint(1,31)
    while ((rs3 is not None) and ((rs3 == rs1) or (rs3 == rs2)) and allunique):
      rs3 = randint(1,31)
    # choose rd that is different than rs1 and rs2 and rs3
    rd = rs1
    while ((rd == rs1) or (rd == rs2) or ((rs3 is not None) and (rd == rs3))):
      rd = randint(1, 31)
    rs1val = randint(0, 2**xlen-1)
    rs2val = randint(0, 2**xlen-1)
    immval = randint(0, 2**xlen-1)
    rdval = randint(0, 2**xlen-1)
    if (rs3 is None): return [rs1, rs2, rd, rs1val, rs2val, immval, rdval]
    else: return [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval]

def make_rd(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cp_rd (Test destination rd = x" + str(r) + ")"
    writeCovVector(desc, rs1, rs2, r, rs1val, rs2val, immval, rdval, test, xlen)

def make_fd(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    desc = "cp_fd (Test destination fd = x" + str(r) + ")"
    writeCovVector(desc, rs1, rs2, r, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_fs1(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    while (r == rs2):
      rs2 = randint(1,31)
    desc = "cp_fs1 (Test source fs1 = f" + str(r) + ")"
    writeCovVector(desc, r, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_fs2(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    while (r == rs1):
      rs1 = randint(1,31)
    desc = "cp_fs2 (Test source fs2 = f" + str(r) + ")"
    writeCovVector(desc, rs1, r, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_fs3(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    while (r == rs1):
      rs1 = randint(1,31)
    desc = "cp_fs3 (Test source fs3 = f" + str(r) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=r, rs3val=rs3val)

def make_rs1(test, xlen, rng = range(32), fli=False):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize(rs1=r, allunique=True)
    desc = "cp_rs1 (Test source rs1 = x" + str(r) + ")"
    if fli:
      desc = f"cp_rs1_fli (Immediate = {flivals[r]} with rs1 encoding 5'b{format(r, f'05b')})"
    writeCovVector(desc, r, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen)

def make_rs2(test, xlen, rng = range(32)):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize(rs2=r, allunique=True)
    while(r == rs1):
      rs1 = randint(1, 31)
    desc = "cp_rs2 (Test source rs2 = x" + str(r) + ")"
    writeCovVector(desc, rs1, r, rd, rs1val, rs2val, immval, rdval, test, xlen)

def make_uimm(test, xlen):
  for r in range(xlen):
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize(allunique=True)
    desc = "cp_uimm (Test bit = " + str(r) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, r, rdval, test, xlen)

def make_uimm5(test, xlen):
  for r in range(32):
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize(allunique=True)
    desc = "cp_uimm_5 (Test bit = " + str(r) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, r, rdval, test, xlen)

def make_rd_rs1(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = f"cmp_rd_rs1 (Test rd = rs1 = x{r})"
    writeCovVector(desc, r, rs2, r, rs1val, rs2val, immval, rdval, test, xlen)

def make_rd_rs2(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cmp_rd_rs2 (Test rd = rs1 = x" + str(r) + ")"
    writeCovVector(desc, rs1, r, r, rs1val, rs2val, immval, rdval, test, xlen)

def make_rd_rs1_rs2(test, xlen):
  for r in range(32):
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cmp_rd_rs1_rs2 (Test rd = rs1 = rs2 = x" + str(r) + ")"
    writeCovVector(desc, r, r, r, rs1val, rs2val, immval, rdval, test, xlen)

def make_rs1_rs2(test, xlen, rng):
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cmp_rs1_rs2 (Test rs1 = rs2 = x" + str(r) + ")"
    writeCovVector(desc, r, r, rd, rs1val, rs2val, immval, rdval, test, xlen)

def make_rs1_corners(test, xlen):
  for v in corners:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cp_rs1_corners (Test source rs1 value = " + hex(v) + ")"
    if ((test in cbptype) or (test in citype)):
      writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, v, test, xlen)
    else:
      writeCovVector(desc, rs1, rs2, rd, v, rs2val, immval, rdval, test, xlen)

def make_rs2_corners(test, xlen):
    for v in corners:
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      if test in ["c.swsp", "c.sdsp"]:
        while (rs2 == 2):
          rs2 = randint(0,31)
      desc = "cp_rs2_corners (Test source rs2 value = " + hex(v) + ")"
      writeCovVector(desc, rs1, rs2, rd, rs1val, v, immval, rdval, test, xlen)

def make_rd_corners(test, xlen, corners):
  if test in c_shiftitype:
    for v in corners:
      # rs1 = all 1s, rs2 = v, others are random
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + " Shifted by 1)"
      writeCovVector(desc, rs1, rs2, rd, -1, v, 1, rdval, test, xlen)
  elif test in catype:   # Using rs1val as temp variable to pass rd value
    for v in corners:
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      while (legalizecompr(rd) == legalizecompr(rs2)):
        rs2 = randint(0,31)
      if test in ["c.or","c.addw","c.xor"]:
        rd_temp = 0
        rs2_temp = v
      elif test in ["c.and"]:
        rd_temp = -1
        rs2_temp = v
      elif test in ["c.mul"]:
        rd_temp = 1
        rs2_temp = v
      elif test in ["c.sub","c.subw"]:
        rd_temp =  v>>1
        rs2_temp = (-v)>>1
      writeCovVector(desc, rs1, rs2, rd, rd_temp, rs2_temp, 0, rdval, test, xlen)
  elif test in crtype:
    for v in corners:
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      rs2val = -(rdval - v)
      writeCovVector(desc, rs1, rs2, rd, 0, rs2val, 0, rdval, test, xlen)
  elif (test == "c.addiw" or test == "c.addi"):
    for v in corners:
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      immval = int(signedImm6(immval))
      rdval = v - immval
      rdval &= 0xFFFFFFFFFFFFFFFF   # This prevents -ve decimal rdval (converts -10 to 18446744073709551606)
      writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen)

  elif (test == "divw" or test == "divuw" or test=="mulw"):
    for v in corners:
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      writeCovVector(desc, rs1, rs2, rd, v, 1, v, rdval, test, xlen)


  elif (test == "c.lui"):
    for v in corners:
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      writeCovVector(desc, rs1, rs2, rd, v, v, v, rdval, test, xlen)
  else:
    for v in corners:
      # rs1 = 0, rs2 = v, others are random
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      writeCovVector(desc, rs1, 0, rd, v, rs2val, 0, rdval, test, xlen)
      # rs1, rs2 = v, others are random
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      writeCovVector(desc, rs1, rs2, rd, v, v, v, rdval, test, xlen)
      # rs1 = all 1s, rs2 = v, others are random
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cp_rd_corners (Test rd value = " + hex(v) + ")"
      writeCovVector(desc, rs1, rs2, rd, -1, v, -1, rdval, test, xlen)

def make_rd_corners_lui(test, xlen, corners):
  for v in corners:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    desc = "cp_rd_corners_lui (Test rd value = " + hex(v) + ")"
    writeCovVector(desc, rs1, rs2, rd,rs1val, rs2val, v>>12, rdval, test, xlen)

def make_rd_rs1_eqval(test, xlen):
  [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
  desc = "cmp_rdm_rs1_eqval (Test rs1 = rd = " + hex(rs1val) + ")"
  writeCovVector(desc, rs1, 0, rd, rdval, rs2val, immval, rdval, test, xlen)

def make_rd_rs2_eqval(test, xlen):
  [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
  desc = "cmp_rd_rs2_eqval (Test rs2 = rd = " + hex(rdval) + ")"
  writeCovVector(desc, 0, rs2, rd, rdval, rdval, immval, rdval, test, xlen)

def make_rs1_rs2_eqval(test, xlen):
  [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
  desc = "cmp_rs1_rs2_eqval (Test rs1 = rs2 = " + hex(rs1val) + ")"
  writeCovVector(desc, rs1, rs2, rd, rs1val, rs1val, immval, rdval, test, xlen)

def make_cp_gpr_hazard(test, xlen):
  if insMap[findInstype('instructions', test, insMap)].get('compressed', 0) != 0:
    print ("hazard tests for compressed instructions will require a major refactor, holding off for now")
    return
  if findInstype('instructions', test, insMap) == 'csrtype' or findInstype('instructions', test, insMap) == 'csritype':
    print("Zicsr hazards not yet implemented")
    return
  for haz in ["nohaz", "raw", "waw", "war"]:
    for src in range(1, 4):
      [rs1a, rs2a, rs3a, rda, rs1vala, rs2vala, rs3vala, immvala, rdvala] = randomize(rs3=True)
      [rs1b, rs2b, rs3b, rdb, rs1valb, rs2valb, rs3valb, immvalb, rdvalb] = randomize(rs3=True)
      # set up hazard
      regsA, regsB = make_unique_hazard(test, regsA=[rda, rs1a, rs2a, rs3a], haz_type=haz, regchoice=src)
      [rda, rs1a, rs2a, rs3a] = regsA
      [rdb, rs1b, rs2b, rs3b] = regsB

      desc = "cp_gpr/fpr_hazard " + haz + " test"

      writeHazardVector(desc, rs1a, rs2a, rda, rs1b, rs2b, rdb, test, immvala, immvalb, src, rs3a=rs3a, rs3b=rs3b, haz_type=haz, xlen=xlen)

def make_rs1_sign(test, xlen):
   for v in [1, -1]:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    rs1val = abs(rs1val % 2**(xlen-1)) * v;
    desc = "cp_rs1_sign (Test source rs1 value = " + hex(rs1val) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen)

def make_rs2_sign(test, xlen):
  for v in [1, -1]:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    rs2val = abs(rs2val % 2**(xlen-1)) * v;
    desc = "cp_rs2_sign (Test source rs2 value = " + hex(rs2val) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen)

def make_cr_rs1_rs2_corners(test, xlen):
  for v1 in corners:
    for v2 in corners:
      # select distinct rs1 and rs2
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      while rs1 == rs2:
        [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      desc = "cr_rs1_rs2_corners (Test source rs1 = " + hex(v1) + " rs2 = " + hex(v2) + ")"
      writeCovVector(desc, rs1, rs2, rd, v1, v2, immval, rdval, test, xlen)

def make_imm_zero(test, xlen):
  [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
  desc = "cp_imm_zero"
  writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, 0, rdval, test, xlen)

def make_imm_corners_jal(test, xlen):
  if (test == "jal"):
    minrng = 3
    maxrng = 14 # testing all 20 bits of immediate is too much code
  elif (test in ["c.jal", "c.j"]):
    f.write("\n.align 2" + " # Start at an address multiple of 4. Required for covering 2 byte jump.\n")
    minrng = 2
    maxrng = 13
  rng = range(minrng,maxrng)
  # Test smallest offset as special case
  lines = "\n# Testcase cp_imm_corners_jal "+str(minrng-1)+"\n"
  lines = lines + ".align " + str(maxrng) + "\n # start all tests on a multiple of the largest one\n"
  if (test == "jal"):
    lines = lines + test + " x1, 1f\n"
  else:
    lines = lines + test + " 1f\n"  # c.jal, c.j
  lines = lines + "1: \n"
  if (test == "jal"):
    lines = lines + test + " x1, f"+str(minrng)+"_"+test+"\n"
  else:
    lines = lines + test + " f"+str(minrng)+"_"+test+"\n"  # c.jal, c.j
  f.write(lines)
  for r in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    lines = "\n# Testcase cp_imm_corners_jal " + str(r) + "\n"
    lines = lines + ".align " + str(r-1) + "\n"
    lines = lines + "b"+ str(r-1)+"_"+test+":\n"
    if (test == "jal"):
      lines = lines + "jal x"+str(rd)+", f"+str(r+1)+"_"+test+" # jump to aligned address to stress immediate\n"
    elif (test in ["c.jal", "c.j"]):
      lines = lines + test + " f"+str(r+1)+"_"+test+" # jump to aligned address to stress immediate\n"
    lines = lines + ".align " + str(r-1) + "\n"
    lines = lines + "f" +str(r)+"_"+test+":\n"
    if (test == "jal"):
      lines = lines + "jal x"+str(rd)+", b"+str(r-1)+"_"+test+" # jump to aligned address to stress immediate\n"
    elif (test in ["c.jal", "c.j"]):
      if (r == 12): # temporary fix for bug in compressed branches
        if (test == "c.j"):
          lines = lines + ".half 0xB001 # backward j by -2048 to b12; GCC is not generating this compressed branch properly per https://github.com/riscv-collab/riscv-gnu-toolchain/issues/1647\n"
        else:
          lines = lines + ".half 0x3001 # backward jal by -2048 to b12; GCC is not generating this compressed branch properly per https://github.com/riscv-collab/riscv-gnu-toolchain/issues/1647\n"
          #lines = lines + test + " b"+str(r-1)+"_"+test+" # jump to aligned address to stress immediate\n"
      else:
        lines = lines + test + " b"+str(r-1)+"_"+test+" # jump to aligned address to stress immediate\n"
    f.write(lines)
  lines = ".align " + str(maxrng-1) + "\n"
  lines = "f"+str(maxrng)+"_"+test+":\n"
  f.write(lines)

def make_imm_corners_jalr(test, xlen):
  for immval in corners_imm_12bit:
    if (immval == 0):
      continue
    [rs1, rs2, rd, rs1val, rs2val, dummy, rdval] = randomize()
    lines = "\n# Testcase cp_imm_corners jalr " + str(immval) + " bin\n"
    lines = lines + "la x"+str(rs1)+", 1f\n" #load the address of the label '1' into x21
    if (immval == -2048):
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 2047 # increment rs1 by 2047 \n" # ***
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", 1 # increment rs1 to bump it by a total of 2048 to compensate for -2048\n"
    else:
      lines = lines + "addi x" + str(rs1) + ", x" + str(rs1) + ", " + signedImm12(-immval) + " # sub immediate from rs1 to counter offset\n"
    lines = lines + "jalr x"+str(rd) + ", x" + str(rs1) + ", "+ signedImm12(immval) +" # jump to assigned address to stress immediate\n" # jump to the label using jalr
    lines = lines + "1:\n"
    f.write(lines)

def make_offset(test, xlen):
  lines = "\n# Testcase cp_offset\n"
  if (test in btype):
    lines = lines + "j 2f # jump past backward branch target\n"
    lines = lines + "1: j 3f # backward branch target: jump past backward branch\n"
    lines = lines + "2: " + test + " x0, x0, 1b # backward branch\n"
  elif (test in crtype):
    lines = lines + "j 2f # jump past backward branch target\n"
    lines = lines + "1: j 3f # backward branch target: jump past backward branch\n"
    rs1 = randint(1, 31)
    lines = lines + "2: " + "la x" + str(rs1) + ", 1b\n"
    lines = lines + test + " x" + str(rs1) + " # backward branch\n"
  elif (test in cjtype):
    lines = lines + "j 2f # jump past backward branch target\n"
    lines = lines + "1: j 3f # backward branch target: jump past backward branch\n"
    lines = lines + "2: " + "nop\n"
    lines = lines + test + " 1b" + " # backward branch\n"
  elif (test in cbtype):
    lines = lines + "j 2f # jump past backward branch target\n"
    lines = lines + "1: j 3f # backward branch target: jump past backward branch\n"
    rs1val = 0 if test == "c.beqz" else 1  # This makes sure branch is taken for both beqz & bnez
    lines = lines + "2: " + f"li x8, {rs1val}" + f" # initialize rs1 to {rs1val}\n"
    lines = lines + test + " x8,  1b # backward branch\n"
  lines = lines + "3: nop # done with sequence\n"
  f.write(lines)

def make_offset_lsbs(test, xlen):
  lines = "\n# Testcase cp_offset_lsbs\n"
  if (test in jalrtype):
    lines = lines + "la x3, jalrlsb1 # load address of label\n"
    lines = lines + "jalr x1, x3, 1 # jump to label + 1, extra plus 1 should be discarded\n"
    lines = lines + "nop # something to skip over\n"
    lines = lines + "jalrlsb1: \n"
    lines = lines + "la x3, jalrlsb2 # load address of label\n"
    lines = lines + "addi x3, x3, 3 # add 3 to address\n"
    lines = lines + "jalr x1, x3, -2 # jump to label + 1, extra plus 1 should be discarded\n"
    lines = lines + "nop # something to skip over\n"
    lines = lines + "jalrlsb2: \n"
  else: # c.jalr / c.jr
    lines = lines + "la x3, "+test+"lsb00 # load address of label\n"
    lines = lines + test + " x3 # jump to address with bottom two lsbs = 00\n"
    lines = lines + "c.nop # something to jump over\n"
    lines = lines + ".align 2\n"
    lines = lines + test+"lsb00: nop\n"
    lines = lines + "la x3, "+test+"lsb01 # load address of label\n"
    lines = lines + "addi x3, x3, 1 # add 1 to address\n"
    lines = lines + test + " x3 # jump to address with bottom two lsbs = 01\n"
    lines = lines + "c.nop # something to jump over\n"
    lines = lines + ".align 2\n"
    lines = lines + test+"lsb01: nop\n"
    lines = lines + "la x3, "+test+"lsb10 # load address of label\n"
    lines = lines + "addi x3, x3, 2 # add 2 to address\n"
    lines = lines + test + " x3 # jump to address with bottom two lsbs = 10\n"
    lines = lines + "c.nop # something to jump over\n"
    lines = lines + ".align 2\n"
    lines = lines + test+"lsb10: nop\n"
    lines = lines + "la x3, "+test+"lsb11 # load address of label\n"
    lines = lines + "addi x3, x3, 3 # add 3 to address\n"
    lines = lines + test + " x3 # jump to address with bottom two lsbs = 11\n"
    lines = lines + "c.nop # something to jump over\n"
    lines = lines + ".align 2\n"
    lines = lines + test+"lsb11: nop\n"
  f.write(lines)

def make_mem_hazard(test, xlen):
  lines = "\n# Testcase mem_hazard (no dependency)\n"
  lines = lines + "la x1, scratch\n"
  lines = lines + test + " x2, 0(x1)\n"
  f.write(lines)

def make_f_mem_hazard(test, xlen):
  lines = "\n# Testcase f_mem_hazard (no dependency)\n"
  lines = lines + "la x1, scratch\n"
  lines = lines + "fsd f2, 0(x1)\n"
  lines = lines + test + " f2, 0(x1)\n"
  f.write(lines)

def make_cp_imm_corners(test, xlen, corners_imm):
  desc = "cp_imm_corners"
  for v1 in corners_imm:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, v1, rdval, test, xlen)

def make_cr_rs1_imm_corners(test, xlen, corners_imm):
  desc = "cr_rs1_imm_corners"
  for v1 in corners:
    for v2 in corners_imm:
      [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
      if ((test in cbptype) or (test in citype)):
        writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, v2, v1, test, xlen)
      else:
        writeCovVector(desc, rs1, rs2, rd, v1, rs2val, v2, rdval, test, xlen)


def make_imm_shift(test, xlen):
  desc = "cp_imm_shift"
  if test in shiftwtype:
    rng = range(1, 32)
  elif test in c_shiftitype:
    rng = range(1, xlen)
  else:
    rng = range(0, xlen)

  for shift in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, shift, rdval, test, xlen)


def make_imm_mul(test, xlen):
  desc = "cp_imm_mul"
  if test in ciwtype:
    rng = range(1,256)
  elif test in citype or test in csstype:
    if test in ["c.lwsp", "c.ldsp", "c.swsp", "c.sdsp","c.flwsp","c.fldsp"]:
      rng = range(64)
    else:
      rng = range(-32,32)
  else:
    rng = range(32)
  for imm in rng:
    [rs1, rs2, rd, rs1val, rs2val, immval, rdval] = randomize()
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, imm, rdval, test, xlen)

def make_fd_fs1(test, xlen, frm=False):
  for r in range(32):
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    if (test.startswith("fsgnj")): # fsgnj with fs1 = fs2 is fmv, so don't pick this
      while (rs2 == r):
        rs2 = randint(1, 31)
    desc = "cmp_fd_fs1 (Test fd = fs1 = f" + str(r) + ")"
    writeCovVector(desc, r, rs2, r, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val, frm=frm)

def make_fd_fs2(test, xlen):
  for r in range(32):
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    if (test.startswith("fsgnj")): # fsgnj with fs1 = fs2 is fmv, so don't pick this
      while (rs1 == r):
        rs1 = randint(1, 31)
    desc = "cmp_fd_fs2 (Test fd = fs2 = f" + str(r) + ")"
    writeCovVector(desc, rs1, r, r, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_fd_fs3(test, xlen, frm=False):
  for r in range(32):
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    desc = "cmp_fd_fs3 (Test fd = fs3 = f" + str(r) + ")"
    writeCovVector(desc, rs1, rs2, r, rs1val, rs2val, immval, rdval, test, xlen, rs3=r, rs3val=rs3val, frm=frm)


def make_frm(test, xlen):
  [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
  desc = "cp_frm"
  # *** should sweep the rounding modes, and coverpoints should check they are hit
  writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3, frm=True)

def make_cr_fs1_fs2_corners(test, xlen, frm = False):
  corners = fcorners
  if test[-1] == "h":
    corners = fcornersH
  if test[-1] == "d":
    corners = fcornersD
  for v1 in corners:
    for v2 in corners:
      # select distinct fs1 and fs2
      [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
      while rs1 == rs2:
        [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
      desc = "cr_fs1_fs2_corners (Test source fs1 = " + hex(v1) + " fs2 = " + hex(v2) + ")"
      f.write("fsflagsi 0b00000 # clear all fflags\n")
      writeCovVector(desc, rs1, rs2, rd, v1, v2, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val, frm=frm)

def make_cr_fs1_fs3_corners(test, xlen, frm = False):
  corners = fcorners
  if test[-1] == "h":
    corners = fcornersH
  if test[-1] == "d":
    corners = fcornersD
  for v1 in corners:
    for v2 in corners:
      # select distinct fs1 and fs3
      [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
      desc = "cr_fs1_fs3_corners (Test source fs1 = " + hex(v1) + " fs3 = " + hex(v2) + ")"
      writeCovVector(desc, rs1, rs2, rd, v1, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=v2, frm=frm)

def make_fs1_corners(test, xlen, fcorners, frm = False):
  for v in fcorners:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    while rs2 == rs1:
      rs2 = randint(1, 31)
    desc = "cp_fs1_corners (Test source fs1 value = " + hex(v) + ")"
    if frm:
      desc = "cr_fs1_corners_frm (Test source fs1 value = " + hex(v) + ")"
    if NaNBox_tests:
      desc = f"Improper NaNBoxed argument test (Value {hex(v)} in f{rs1})"
    f.write("fsflagsi 0b00000 # clear all fflags\n")
    writeCovVector(desc, rs1, rs2, rd, v, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val, frm = frm)

def make_fs2_corners(test, xlen, fcorners):
  for v in fcorners:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    while rs2 == rs1:
      rs2 = randint(1, 31)
    desc = "cp_fs2_corners (Test source fs2 value = " + hex(v) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, v, immval, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_fs3_corners(test, xlen, fcorners):
  for v in fcorners:
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    desc = "cp_fs3_corners (Test source fs3 value = " + hex(v) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, immval, rdval, test, xlen, rs3=rs3, rs3val=v)

def make_imm5_corners(test, xlen):
  for v in range(32):
    [rs1, rs2, rs3, rd, rs1val, rs2val, rs3val, immval, rdval] = randomize(rs3=True)
    desc = "cp_imm5_corners (Test imm value = " + hex(v) + ")"
    writeCovVector(desc, rs1, rs2, rd, rs1val, rs2val, v, rdval, test, xlen, rs3=rs3, rs3val=rs3val)

def make_bs(test, xlen):
  # TODO: This should iterate over the four values of bs in the aes32 instructions
  pass

def make_rnum(test, xlen):
  # TODO: This should iterate over the 10 values of rnum in the aes64ks1i instructions
  pass

# Python randomizes hashes, while we are trying to have a repeatable hash for repeatable test cases.
# This function gives a simple hash as a random seed.
def myhash(s):
  h = 0
  for c in s:
    h = (h * 31 + ord(c)) & 0xFFFFFFFF
  return h

def write_tests(coverpoints, test, xlen):
  global NaNBox_tests
  for coverpoint in coverpoints:
    # produce a deterministic seed for repeatable random numbers 
    # distinct for each instruction and coverpoint
    testname = test + coverpoint
    hashval = myhash(testname)
    # hashval = hash(testname) # doesn't work because of Python hash randomization
    #print(" Seeding " + testname + " with " + str(hashval))
    seed(hashval)
    #seed(hash(test + coverpoint)) 
    if (coverpoint == "cp_asm_count"):
      if (test == "c.nop" or test == "fence"):   # Writing cp_asm_count for 'c.nop' only
        f.write("\n# Testcase cp_asm_count\n"+test+"\n")
    elif (coverpoint == "cp_rd"):
      make_rd(test, xlen, range(32))
    elif(coverpoint == "cp_rd_nx0" or coverpoint == "cp_rd_nx2"):
      make_rd(test, xlen, range(1,32))
    elif (coverpoint == "cp_rdp"):
      make_rd(test, xlen, range(8, 16))
    elif (coverpoint == "cp_rs1p"):
      make_rs1(test, xlen, range(8, 16))
    elif (coverpoint == "cp_rs2p"):
      make_rs2(test, xlen, range(8, 16))
    elif (coverpoint == "cp_fd"):
      make_fd(test, xlen, range(32))
    elif (coverpoint == "cp_fdp"):
      make_fd(test, xlen, range(8, 16))
    elif (coverpoint == "cp_fs1"):
      make_fs1(test, xlen, range(32))
    elif (coverpoint == "cp_fs1p"):
      make_fs1(test, xlen, range(8, 16))
    elif (coverpoint == "cp_fs2"):
      make_fs2(test, xlen, range(32))
    elif (coverpoint == "cp_fs3"):
      make_fs3(test, xlen, range(32))
    elif (coverpoint == "cp_fs2p"):
      make_fs2(test, xlen, range(8, 16))
    elif (coverpoint == "cp_fs1_corners"):
      make_fs1_corners(test, xlen, fcorners)
    elif (coverpoint == "cp_fs2_corners"):
      make_fs2_corners(test, xlen, fcorners)
    elif (coverpoint == "cp_fs3_corners"):
      make_fs3_corners(test, xlen, fcorners)
    elif (coverpoint == "cp_fs1_corners_D"):
      make_fs1_corners(test, xlen, fcornersD)
    elif (coverpoint == "cp_fs2_corners_D"):
      make_fs2_corners(test, xlen, fcornersD)
    elif (coverpoint == "cp_fs3_corners_D"):
      make_fs3_corners(test, xlen, fcornersD)
    elif (coverpoint == "cp_fs1_corners_H"):
      make_fs1_corners(test, xlen, fcornersH)
    elif (coverpoint == "cp_fs2_corners_H"):
      make_fs2_corners(test, xlen, fcornersH)
    elif (coverpoint == "cp_fs3_corners_H"):
      make_fs3_corners(test, xlen, fcornersH)
    # elif (coverpoint == "cp_fs1_corners_Q"):
    #   make_fs1_corners(test, xlen, fcornersQ)
    # elif (coverpoint == "cp_fs2_corners_Q"):
    #   make_fs2_corners(test, xlen, fcornersQ)
    # elif (coverpoint == "cp_fs3_corners_Q"):
    #   make_fs3_corners(test, xlen, fcornersQ)
    elif (coverpoint == "cp_rs1"):
      make_rs1(test, xlen, range(32))
    elif (coverpoint == "cp_rs1_nx0"):
      make_rs1(test, xlen, range(1,32))
    elif (coverpoint == "cp_rs2"):
      make_rs2(test, xlen, range(32))
    elif (coverpoint == "cp_rs2_nx0"):
      make_rs2(test, xlen, range(1,32))
    elif (coverpoint == "cp_uimm"):
      make_uimm(test, xlen)
    elif (coverpoint == "cp_uimm_5"):
      make_uimm5(test, xlen)
    elif (coverpoint == "cmp_rd_rs1"):
      make_rd_rs1(test, xlen, range(32))
    elif (coverpoint == "cmp_rd_rs1_nx0"):
      make_rd_rs1(test, xlen, range(1,32))
    elif (coverpoint == "cmp_rd_rs1_c"):
      make_rd_rs1(test, xlen, range(8, 16))
    elif (coverpoint == "cmp_rd_rs2"):
      make_rd_rs2(test, xlen, range(32))
    elif (coverpoint == "cmp_rd_rs2_nx0"):
      make_rd_rs2(test, xlen, range(1,32))
    elif (coverpoint == "cmp_rd_rs2_c"):
      make_rd_rs2(test, xlen, range(8, 16))
    elif (coverpoint == "cmp_rd_rs1_rs2"):
      make_rd_rs1_rs2(test, xlen)
    elif (coverpoint == "cmp_rs1_rs2"):
      make_rs1_rs2(test, xlen, range(32))
    elif (coverpoint == "cmp_rs1_rs2_nx0"):
      make_rs1_rs2(test, xlen, range(1,32))
    elif (coverpoint == "cmp_rs1_rs2_c"):
      make_rs1_rs2(test, xlen, range(8,16))
    elif (coverpoint == "cp_rs1_corners"):
      make_rs1_corners(test, xlen)
    elif (coverpoint == "cp_rs2_corners"):
      make_rs2_corners(test, xlen)
    elif (coverpoint == "cp_rd_corners_slli"):
      if (xlen == 32):
        make_rd_corners(test, xlen, c_slli_32_corners)
      else:
        make_rd_corners(test, xlen, c_slli_64_corners)
    elif (coverpoint == "cp_rd_corners_srli"):
      if (xlen == 32):
        make_rd_corners(test, xlen, c_srli_32_corners)
      else:
        make_rd_corners(test, xlen, c_srli_64_corners)
    elif (coverpoint == "cp_rd_corners_srai"):
      if (xlen == 32):
        make_rd_corners(test, xlen, c_srai_32_corners)
      else:
        make_rd_corners(test, xlen, c_srai_64_corners)
    elif (coverpoint == "cp_rd_corners"):
      make_rd_corners(test, xlen, corners)
    elif (coverpoint == "cp_rd_corners_clui"):
      make_rd_corners(test, xlen, corners_6bit)
    elif (coverpoint == "cp_rd_corners_lw" or coverpoint == "cp_rd_corners_lwu"):
      make_rd_corners(test, xlen, corners_32bit)
    elif (coverpoint == "cp_rd_corners_lh" or coverpoint == "cp_rd_corners_lhu"):
      make_rd_corners(test, xlen, corners_16bit)           # Make rd corners for lh and lhu for both RV32I & RV64I
    elif (coverpoint == "cp_rd_corners_lb" or coverpoint == "cp_rd_corners_lbu"):
      make_rd_corners(test, xlen, corners_8bits)            # Make rd corners for lb and lbu for both RV32I & RV64I
    elif (coverpoint == "cp_rd_corners_6bit"):
      make_rd_corners(test, xlen, corners_6bit)
    elif (coverpoint == "cp_rd_corners_32bit"):
      make_rd_corners(test, xlen, corners_32bit)
    elif (coverpoint == "cp_rd_corners_lui"):
      make_rd_corners_lui(test, xlen, corners_20bit)
    elif (coverpoint == "cmp_rd_rs1_eqval"):
      make_rd_rs1_eqval(test, xlen)
    elif (coverpoint == "cmp_rd_rs2_eqval"):
      make_rd_rs2_eqval(test, xlen)
    elif (coverpoint == "cmp_rs1_rs2_eqval"):
      make_rs1_rs2_eqval(test, xlen)
    elif (coverpoint == "cp_rs1_sign"):
      make_rs1_sign(test, xlen)
    elif (coverpoint == "cp_rs2_sign"):
      make_rs2_sign(test, xlen)
    elif (coverpoint == "cp_rd_sign"):
      pass # already covered by rd_corners
    elif (coverpoint == "cr_rs1_rs2_corners"):
      make_cr_rs1_rs2_corners(test, xlen)
    elif (coverpoint == "cp_imm_corners"):
      if (test == "jalr"):
          make_imm_corners_jalr(test, xlen)
      else:
        make_cp_imm_corners(test, xlen, corners_imm_12bit)
    elif (coverpoint == "cp_imm_corners_20bit"):
      make_cp_imm_corners(test, xlen, corners_imm_20bit)
    elif (coverpoint == "cp_imm_corners_6bit"):
      make_cp_imm_corners(test, xlen, corners_imm_6bit)
    elif (coverpoint == "cp_imm_corners_jal"):
      make_imm_corners_jal(test, xlen)
    elif (coverpoint == "cp_imm_corners_c_jal"):
        make_imm_corners_jal(test,xlen)
    elif (coverpoint == "cr_rs1_imm_corners"):
      make_cr_rs1_imm_corners(test, xlen, corners_imm_12bit)
    elif (coverpoint == "cr_rs1_imm_corners_6bit"):
      make_cr_rs1_imm_corners(test, xlen, corners_imm_6bit)
    elif (coverpoint == "cr_rs1_rs2"):
      pass # already covered by cr_rs1_rs2_corners
    elif (coverpoint in ["cp_gpr_hazard", "cp_gpr_hazard_r", "cp_gpr_hazard_rw", "cp_gpr_hazard_w"]):
      make_cp_gpr_hazard(test, xlen)
    elif (coverpoint in ["cp_fpr_hazard", "cp_fpr_hazard_r", "cp_fpr_hazard_rw", "cp_fpr_hazard_w"]):
      make_cp_gpr_hazard(test, xlen)
    elif (coverpoint == "cp_fclass"):
      pass
    elif (coverpoint == "cp_imm_sign"):
      make_imm_zero(test, xlen)
    elif (coverpoint == "cp_imm_sign_clui"):
      pass
    elif (coverpoint == "cp_rd_corners_sraiw"):
      make_rd_corners(test,xlen,corners_sraiw)
    elif (coverpoint == "cp_mem_hazard"):
      make_mem_hazard(test, xlen)
    elif (coverpoint == "cp_f_mem_hazard"):
      make_f_mem_hazard(test, xlen)
    elif (coverpoint == "cp_imm_zero"):
      make_imm_zero(test, xlen)
    elif (coverpoint == "cp_mem_unaligned"):
      pass # seems this should be part of privileged tests
    elif (coverpoint == "cp_offset"):
      make_offset(test, xlen)
    elif (coverpoint == "cp_offset_lsbs"):
      make_offset_lsbs(test, xlen)
    elif (coverpoint == "cr_nord_rs1_rs2"):
      pass #TODO (not if crosses are not needed)
    elif (coverpoint == "cp_imm_shift" or coverpoint == "cp_imm_shift_c" or coverpoint == "cp_imm_shift_w"):
      make_imm_shift(test, xlen)
    elif coverpoint in ["cp_imm_mul","cp_imm_mul_8","cp_imm_mul_addi4spn","cp_imm_mul_addi16sp","cp_imm_mul_4sp","cp_imm_mul_8sp"]:
      make_imm_mul(test, xlen)
    elif (coverpoint == "cp_rd_boolean"):
      pass # covered by other generators
    elif (coverpoint == "cmp_fd_fs1"):
      make_fd_fs1(test, xlen)
    elif (coverpoint == "cmp_fd_fs2"):
      make_fd_fs2(test, xlen)
    elif (coverpoint == "cmp_fd_fs3"):
      make_fd_fs3(test, xlen)
    # elif (coverpoint == "cp_fs1_corners"):
    #   make_fs1_corners(test, xlen)
    # elif (coverpoint == "cp_fs2_corners"):
    #   make_fs2_corners(test, xlen)
    elif (coverpoint in ["cr_fs1_fs2_corners", "cr_fs1_fs2_corners_H", "cr_fs1_fs2_corners_D"]):
      make_cr_fs1_fs2_corners(test, xlen)
    elif (coverpoint in ["cr_fs1_fs2_corners_frm", "cr_fs1_fs2_corners_frm_H", "cr_fs1_fs2_corners_frm_D"]):
      make_cr_fs1_fs2_corners(test, xlen, frm = True)
    elif (coverpoint in ["cr_fs1_fs2_corners_frm4", "cr_fs1_fs2_corners_frm4_H", "cr_fs1_fs2_corners_frm4_D"]):
      make_cr_fs1_fs2_corners(test, xlen, frm = True)
    elif (coverpoint in ["cr_fs1_fs3_corners_frm", "cr_fs1_fs3_corners_frm_H", "cr_fs1_fs3_corners_frm_D"]):
      make_cr_fs1_fs3_corners(test, xlen, frm = True)
    elif (coverpoint in ["cr_fs1_fs3_corners_frm4", "cr_fs1_fs3_corners_frm4_H", "cr_fs1_fs3_corners_frm4_D"]):
      make_cr_fs1_fs3_corners(test, xlen, frm = True)
    elif (coverpoint in ["cp_frm_2", "cp_frm_3", "cp_frm_4"]):
      make_frm(test, xlen)
    elif (coverpoint == "cr_fs1_corners_frm"):
      make_fs1_corners(test, xlen, fcorners, frm=True)
    elif (coverpoint == "cr_fs1_corners_frm_D"):
      make_fs1_corners(test, xlen, fcornersD, frm=True)
    elif (coverpoint == "cr_fs1_corners_frm_H"):
      make_fs1_corners(test, xlen, fcornersH, frm=True)
    elif (coverpoint.startswith("cp_csr_fflags")):
      pass # doesn't require designated tests
    elif (coverpoint == "cp_csr_frm"):
      pass # already covered by cp_frm tests
    elif (coverpoint.startswith("cp_NaNBox")):
      pass # doesn't require designated tests
    elif (coverpoint == "cp_rs1_fli"):
      make_rs1(test, xlen, range(32), fli=True)
    elif (coverpoint == "cp_fs1_badNB_D_S"):
      NaNBox_tests = "D"
      make_fs1_corners(test, xlen, badNB_corners_D_S)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs2_badNB_D_S"):
      NaNBox_tests = "D"
      make_fs2_corners(test, xlen, badNB_corners_D_S)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs3_badNB_D_S"):
      NaNBox_tests = "D"
      make_fs3_corners(test, xlen, badNB_corners_D_S)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs1_badNB_D_H"):
      NaNBox_tests = "D"
      make_fs1_corners(test, xlen, badNB_corners_D_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs2_badNB_D_H"):
      NaNBox_tests = "D"
      make_fs2_corners(test, xlen, badNB_corners_D_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs3_badNB_D_H"):
      NaNBox_tests = "D"
      make_fs3_corners(test, xlen, badNB_corners_D_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs1_badNB_S_H"):
      NaNBox_tests = "S"
      make_fs1_corners(test, xlen, badNB_corners_S_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs2_badNB_S_H"):
      NaNBox_tests = "S"
      make_fs2_corners(test, xlen, badNB_corners_S_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_fs3_badNB_S_H"):
      NaNBox_tests = "S"
      make_fs3_corners(test, xlen, badNB_corners_S_H)
      NaNBox_tests = False
    elif (coverpoint == "cp_imm5_corners"):
      make_imm5_corners(test, xlen)
    elif (coverpoint == "cp_bs"):
      make_bs(test, xlen)
    elif (coverpoint == "cp_rnum"):
      make_rnum(test, xlen)
    elif (coverpoint == "cp_sc"):
      pass # TODO does this need to be implemented?
    else:
      print("Warning: " + coverpoint + " not implemented yet for " + test)

def getcovergroups(coverdefdir, coverfiles, xlen):
  coverpoints = {}
  curinstr = ""
  mode = "both"
  ingroup = False
  for coverfile in coverfiles:
    coverfile = coverdefdir + "/" + coverfile + "_coverage.svh"
    f = open(coverfile, "r")
    for line in f:
      if (re.search("covergroup .* with", line)):
        ingroup = True
      if (re.search("endgroup", line)):
        ingroup = False
      if ((not ingroup) and re.search('`ifdef XLEN32', line)):
        mode = 32
      if ((not ingroup) and re.search('`ifdef XLEN64', line)):
        mode = 64

      # only look for coverpoints if we are of the proper xlen
      #print("mode: " + str(mode) + " xlen: " + str(xlen) + " " + line)
      if (mode == "both" or mode == xlen):
        m = re.search(r'cp_asm_count.*\"(.*)"', line)
        if (m):
          curinstr = m.group(1)
          coverpoints[curinstr] = []
        m = re.search("\s*(\S+) :", line)
        if (m):
          coverpoints[curinstr].append(m.group(1))
    f.close()
    # print(coverpoints)
    return coverpoints
  
def getExtensions():
  extensions = []
  path = ARCH_VERIF+"/fcov/unpriv"
  for (dirpath, dirnames, filenames) in os.walk(path):
    for filename in filenames:
      m = re.search("(.*)_coverage.svh", filename)
      if (m != None):
        extensions.append(m.group(1))
  return extensions

##################################
# main body
##################################

# change these to suite your tests
ARCH_VERIF = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
rtype = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and",
        "addw", "subw", "sllw", "srlw", "sraw",
        "mul", "mulh", "mulhsu", "mulhu", "div", "divu", "rem", "remu",
        "mulw", "divw", "divuw", "remw", "remuw",
        "czero.eqz", "czero.nez",
        "sh1add", "sh2add", "sh3add",
        "sh1add.uw", "sh2add.uw", "sh3add.uw", "add.uw",
        "min", "minu", "max", "maxu", "orn", "andn", "xnor", "rol", "ror",
        "rolw", "rorw",
        "clmul", "clmulh", "clmulr",
        "bclr", "binv", "bset", "bext",
        "pack", "packh", "packw",
        "xperm4", "xperm8",
        "aes64es", "aes64esm", "aes64ds", "aes64dsm", "aes64ks2",
        "sha512sig0h", "sha512sig0l", "sha512sig1h", "sha512sig1l", "sha512sum0r", "sha512sum1r"]

i1type=["orc.b", "zext.h", "clz", "cpop", "ctz", "sext.b", "sext.h", "rev8",
        "clzw", "cpopw", "ctzw",
        "brev8", "zip", "unzip",
        "aes64im",
        "sha256sig0", "sha256sig1", "sha256sum0", "sha256sum1", 
        "sha512sig0", "sha512sig1", "sha512sum0", "sha512sum1"]
rbtype = ["aes32dsi", "aes32dsmi", "aes32esi", "aes32esmi"]
irtype = ["aes64ks1i"]
lrtype = ["lr.w", "lr.d"]
sctype = ["sc.w", "sc.d"]
amotype = ["amoswap.w", "amoadd.w", "amoand.w", "amoor.w", "amoxor.w", "amomin.w", "amomax.w", "amominu.w", "amomaxu.w",
           "amoswap.d", "amoadd.d", "amoand.d", "amoor.d", "amoxor.d", "amomin.d", "amomax.d", "amominu.d", "amomaxu.d"]

loaditype = ["lb", "lh", "lw", "ld", "lbu", "lhu", "lwu"]
shiftitype = ["slli", "srli", "srai"]
shiftiwtype = ["slliw", "srliw", "sraiw"]
itype = ["addi", "slti", "sltiu", "xori", "ori", "andi", "addiw"]
ibtype = ["slli.uw","bclri","binvi","bseti","bexti","rori"]
ibwtype = ["roriw"]
stype = ["sb", "sh", "sw", "sd"]
btype = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]
jtype = ["jal"]
jalrtype = ["jalr"]
utype = ["lui", "auipc"]
fltype = ["flw",
          "flh",
          "fld"]
fstype = ["fsw",
          "fsh",
          "fsd"]
F2Xtype = ["fcvt.w.s", "fcvt.wu.s", "fmv.x.w", "fcvt.l.s", "fcvt.lu.s",
            "fcvt.w.h", "fcvt.wu.h", "fmv.x.h", "fcvt.l.h", "fcvt.lu.h",
            "fcvt.w.d", "fcvt.wu.d", "fmv.x.d", "fcvt.l.d", "fcvt.lu.d", "fmvh.x.d", "fcvtmod.w.d"]
fr4type = ["fmadd.s", "fmsub.s", "fnmadd.s", "fnmsub.s",
            "fmadd.h", "fmsub.h", "fnmadd.h", "fnmsub.h",
            "fmadd.d", "fmsub.d", "fnmadd.d", "fnmsub.d"]
frtype = ["fadd.s", "fsub.s", "fmul.s", "fdiv.s", "fsgnj.s", "fsgnjn.s", "fsgnjx.s", "fmax.s", "fmin.s", "fminm.s", "fmaxm.s",
          "fadd.h", "fsub.h", "fmul.h", "fdiv.h", "fsgnj.h", "fsgnjn.h", "fsgnjx.h", "fmax.h", "fmin.h", "fminm.h", "fmaxm.h",
          "fadd.d", "fsub.d", "fmul.d", "fdiv.d", "fsgnj.d", "fsgnjn.d", "fsgnjx.d", "fmax.d", "fmin.d", "fminm.d", "fmaxm.d",]
fitype = ["fsqrt.s", "fround.s", "froundnx.s",
          "fsqrt.h", "fround.h", "froundnx.h",
          "fsqrt.d", "fround.d", "froundnx.d",
          "fcvt.s.h", "fcvt.h.s",
          "fcvt.s.d", "fcvt.d.s",
          "fcvt.d.h", "fcvt.h.d"]
fixtype = ["fclass.s",
            "fclass.h",
            "fclass.d"]
X2Ftype = ["fcvt.s.w", "fcvt.s.wu", "fmv.w.x", "fcvt.s.l", "fcvt.s.lu",
            "fcvt.h.w", "fcvt.h.wu", "fmv.h.x", "fcvt.h.l", "fcvt.h.lu",
            "fcvt.d.w", "fcvt.d.wu", "fmv.d.x", "fcvt.d.l", "fcvt.d.lu"]
PX2Ftype = ["fmvp.d.x"] # pair of integer registers to a single fp register
fcomptype = ["feq.s", "flt.s", "fle.s", "fltq.s", "fleq.s",
              "feq.h", "flt.h", "fle.h", "fltq.h", "fleq.h",
              "feq.d", "flt.d", "fle.d", "fltq.d", "fleq.d",]
citype = ["c.nop", "c.lui", "c.li", "c.addi", "c.addi16sp", "c.addiw","c.lwsp","c.ldsp","c.flwsp","c.fldsp"]
c_shiftitype = ["c.slli","c.srli","c.srai"]
cltype = ["c.lw","c.ld","c.flw","c.fld"]
cstype = ["c.sw","c.sd","c.fsw","c.fsd"]
csstype = ["c.sdsp","c.swsp","c.fswsp","c.fsdsp"]
crtype = ["c.add", "c.mv", "c.jalr", "c.jr"]
ciwtype = ["c.addi4spn"]
cjtype = ["c.j","c.jal"]
catype = ["c.sub","c.or","c.and","c.xor","c.subw","c.addw","c.mul"]
cbptype = ["c.andi"]
cbtype = ["c.beqz", "c.bnez"]
shiftwtype = ["sraiw", "srliw"]
csbtype = ["c.sb"]
cshtype = ["c.sh"]
clhtype = ["c.lh","c.lhu"]
clbtype = ["c.lbu"]
cutype = ["c.not","c.zext.b","c.zext.h","c.zext.w","c.sext.b","c.sext.h"]
zcftype = ["c.flw", "c.fsw","c.flwsp","c.fswsp"] # Zcf instructions
zcdtype = ["c.fld", "c.fsd","c.fsdsp","c.fldsp"]
flitype = ["fli.s", "fli.h", "fli.d"] # technically FI type but with a strange "immediate" encoding, need special cases
csrtype = ["csrrw", "csrrs", "csrrc"]
csritype = ["csrrwi", "csrrsi", "csrrci"]

floattypes = frtype + fstype + fltype + fcomptype + F2Xtype + fr4type + fitype + fixtype + X2Ftype + zcftype + flitype + PX2Ftype + zcdtype
# instructions with all float args
regconfig_ffff = frtype + fr4type + fitype + flitype
# instructions with int first arg and the rest float args
regconfig_xfff = F2Xtype + fcomptype + fixtype
# instructions with fp first arg and the rest int args
regconfig_fxxx = X2Ftype + PX2Ftype

global hazardLabel
hazardLabel = 1

# for writeHazardVectors
rd_rs1_rs2_format = rtype + frtype + fcomptype + PX2Ftype
rd_rs1_imm_format = shiftitype + shiftiwtype + itype + utype + shiftwtype
rd_rs1_rs2_rs3_format = fr4type
rd_rs1_format = F2Xtype + X2Ftype + fitype + fixtype + crtype + catype + cutype
rd_imm_format = citype + cstype + ciwtype + cbptype


insMap = {
  # 'loadstore': whether a function is a load or store, leave empty for neither
  # 'compressed': 3 levels, which are 0 for uncompressed (implicit value), 1 for compressed instruction,
  #   2 for compressed instruction with 3-bit register fields
  # 'implicitxreg': which reads and writes don't appear in the instruction fields but still occur
  #   once the instruction is expanded
  'rtype' : {'instructions' : rtype, 'regconfig' : 'xxx_'},
  'i1type' : {'instructions' : i1type, 'regconfig' : 'xx__'},
  'rbtype' : {'instructions' : rbtype, 'regconfig' : 'xxx_'},
  'irtype' : {'instructions' : irtype, 'regconfig' : 'xx__'},
  'lrtype' : {'instructions' : lrtype, 'regconfig' : 'xx__'},
  'sctype' : {'instructions' : sctype, 'regconfig' : 'xxx_'},
  'amotype' : {'instructions' : amotype, 'regconfig' : 'xxx_'},
  'loaditype' : {'instructions' : loaditype, 'regconfig' : 'xxi_', 'loadstore' : 'load'},
  'shiftiwtype' : {'instructions' : shiftiwtype, 'regconfig' : 'xxi_'},
  'shiftitype' : {'instructions' : shiftitype, 'regconfig' : 'xxi_'},
  'itype' : {'instructions' : itype, 'regconfig' : 'xxi_'},
  'ibtype' : {'instructions' : ibtype, 'regconfig' : 'xxi_'},
  'ibwtype' : {'instructions' : ibwtype, 'regconfig' : 'xxi_'},
  'stype' : {'instructions' : stype, 'regconfig' : '_xx_', 'loadstore' : 'store'},
  'btype' : {'instructions' : btype, 'regconfig' : '_xxl'},
  'jtype' : {'instructions' : jtype, 'regconfig' : 'xl__'},
  'jalrtype' : {'instructions' : jalrtype, 'regconfig' : 'xxi_'},
  'utype' : {'instructions' : utype, 'regconfig' : 'xi__'},
  'fltype' : {'instructions' : fltype, 'regconfig' : 'fxi_', 'loadstore' : 'load'},
  'fstype' : {'instructions' : fstype, 'regconfig' : '_xfi', 'loadstore' : 'store'},
  'F2Xtype' : {'instructions' : F2Xtype, 'regconfig' : 'xf__'},
  'fr4type' : {'instructions' : fr4type, 'regconfig' : 'ffff'},
  'frtype' : {'instructions' : frtype, 'regconfig' : 'fff_'},
  'fitype' : {'instructions' : fitype, 'regconfig' : 'ff__'},
  'fixtype' : {'instructions' : fixtype, 'regconfig' : 'xf__'},
  'X2Ftype' : {'instructions' : X2Ftype, 'regconfig' : 'fx__'},
  'PX2Ftype' : {'instructions' : PX2Ftype, 'regconfig' : 'fxx_'},
  'fcomptype' : {'instructions' : fcomptype, 'regconfig' : 'xff_'},
  'citype' : {'instructions' : ["c.lui", "c.li", "c.addi", "c.addi16sp", "c.addiw", "c.lwsp", "c.ldsp", "c.flwsp", "c.fldsp"], 'regconfig' : 'xi__', 'compressed' : 1, 'implicitxreg' : '_x__'},
  'cnoptype' : {'instructions' : ["c.nop"], 'regconfig' : '____', 'compressed' : 1, 'implicitxreg' : '____'},
  'c_shiftitype' : {'instructions' : c_shiftitype, 'regconfig' : 'x___', 'compressed' : 1},
  'cltype' : {'instructions' : cltype, 'regconfig' : 'xxi_', 'compressed' : 1, 'loadstore' : 'load'},
  'cstype' : {'instructions' : cstype, 'regconfig' : '_xxi', 'compressed' : 1, 'loadstore' : 'store'},
  'csstype' : {'instructions' : csstype, 'regconfig' : '_x__', 'compressed' : 1, 'loadstore' : 'store'},
  'crtype' : {'instructions' : ['c.add', 'c.mv'], 'regconfig' : 'xx__', 'compressed' : 1},
  'cjrtype' : {'instructions' : ['c.jr', 'c.jalr'], 'regconfig' : '_x__', 'compressed' : 1, 'implicitxreg' : 'x___'},
  'ciwtype' : {'instructions' : ciwtype, 'regconfig' : 'xxi_', 'compressed' : 1},
  'cjtype' : {'instructions' : cjtype, 'regconfig' : 'l___'}, 'compressed' : 1,
  'catype' : {'instructions' : catype, 'regconfig' : 'x_x_', 'compressed' : 2, 'implicitxreg' : '_x__'},
  'cbptype' : {'instructions' : cbptype, 'regconfig' : 'xi__', 'compressed' : 2},
  'cbtype' : {'instructions' : cbtype, 'regconfig' : '_xl_', 'compressed' : 2},
  'shiftwtype' : {'instructions' : shiftwtype, 'regconfig' : 'xx__'},
  'csbtype' : {'instructions' : csbtype, 'regconfig' : '_xxi', 'compressed' : 1, 'loadstore' : 'store'},
  'cshtype' : {'instructions' : cshtype, 'regconfig' : '_xxi', 'compressed' : 1, 'loadstore' : 'store'},
  'clhtype' : {'instructions' : clhtype, 'regconfig' : 'xxi_', 'compressed' : 1, 'loadstore' : 'load'},
  'clbtype' : {'instructions' : clbtype, 'regconfig' : 'xxi_', 'compressed' : 1, 'loadstore' : 'load'},
  'cutype' : {'instructions' : cutype, 'regconfig' : 'x___', 'compressed' : 1},
  'zcftype' : {'instructions' : zcftype, 'regconfig' : 'uuuu'},
  'zcdtype' : {'instructions' : zcdtype, 'regconfig' : 'uuuu'},
  'flitype' : {'instructions' : flitype, 'regconfig' : 'fi__'},
  'csrtype' : {'instructions' : csrtype, 'regconfig' : 'xx__'},
  'csritype' : {'instructions' : csritype, 'regconfig' : 'xi__'}
}

if __name__ == '__main__':
  # map register encodings to literal values for fli.*
  flivals = { 0: -1.0,
              1: "min",
              2: "0x1p-16",
              3: "0x1p-15",
              4: "0x1p-8",
              5: "0x1p-7",
              6: 0.0625,
              7: 0.125,
              8: 0.25,
              9: 0.3125,
             10: 0.375,
             11: 0.4375,
             12: 0.5,
             13: 0.625,
             14: 0.75,
             15: 0.875,
             16: 1.0,
             17: 1.25,
             18: 1.5,
             19: 1.75,
             20: 2.0,
             21: 2.5,
             22: 3.0,
             23: 4.0,
             24: 8.0,
             25: 16.0,
             26: 128.0,
             27: 256.0,
             28: "0x1p15",
             29: "0x1p16",
             30: "inf",
             31: "nan" }

  # TODO: auipc missing, check whatelse is missing in ^these^ types

  author = "David_Harris@hmc.edu"
  xlens = [32, 64]
  numrand = 3
  corners = []
  fcorners = []

  # setup
  seed(0) # make tests reproducible

  # generate files for each test
  for xlen in xlens:
    extensions = getExtensions() # find all extensions in 
    #print(extensions)
    for extension in extensions:
      coverdefdir = f"{ARCH_VERIF}/fcov/unpriv"
      coverfiles = [extension]
      coverpoints = getcovergroups(coverdefdir, coverfiles, xlen)
      #print(extension+": "+str(coverpoints))
      print("Generating tests for " + extension)
      formatstrlen = str(int(xlen/4))
      formatstr = "0x{:0" + formatstrlen + "x}" # format as xlen-bit hexadecimal number
      formatrefstr = "{:08x}" # format as xlen-bit hexadecimal number with no leading 0x
      if (xlen == 32):
        storecmd = "sw"
        wordsize = 4
      else:
        storecmd = "sd"
        wordsize = 8
      if (extension in ["D", "ZfaD", "ZfhD","Zcd"]):
        flen = 64
      else:
        flen = 32
      formatstrlenFP = str(int(flen/4))
      formatstrFP = "0x{:0" + formatstrlenFP + "x}" # format as flen-bit hexadecimal number
      corners = [0, 1, 2, 2**(xlen-1), 2**(xlen-1)+1, 2**(xlen-1)-1, 2**(xlen-1)-2, 2**xlen-1, 2**xlen-2]
      if (xlen == 32):
        corners = corners + [0b01011011101111001000100001110111, 0b10101010101010101010101010101010, 0b01010101010101010101010101010101]
      else:
        corners = corners + [0b0101101110111100100010000111011101100011101011101000011011110111, # random
                             0b1010101010101010101010101010101010101010101010101010101010101010, # walking odd
                             0b0101010101010101010101010101010101010101010101010101010101010101, # walking even
                             0b0000000000000000000000000000000011111111111111111111111111111111, # Wmax
                             0b0000000000000000000000000000000011111111111111111111111111111110, # Wmaxm1
                             0b0000000000000000000000000000000100000000000000000000000000000000, # Wmaxp1
                             0b0000000000000000000000000000000100000000000000000000000000000001] # Wmaxp2

        corners_sraiw = [0b0000000000000000000000000000000000000000000000000000000000000000,
                         0b0000000000000000000000000000000000000000000000000000000000000001,
                         0b1111111111111111111111111111111111111111111111111111111111111111,
                         0b0000000000000000000000000000000001111111111111111111111111111111,
                         0b1111111111111111111111111111111110000000000000000000000000000000]


      corners_imm_12bit = [0, 1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1023, 1024, 1795, 2047, -2048, -2047, -2, -1]
      corners_imm_20bit = [0, 1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524286, 524287, 524288, 524289, 1048574, 1048575]
      corners_16bit = [0, 1, 2, 2**(15), 2**(15)+1,2**(15)-1, 2**(15)-2, 2**(16)-1, 2**(16)-2,
                    0b0101010101010101, 0b1010101010101010, 0b0101101110111100, 0b1101101110111100]
      corners_8bits = [0, 1, 2, 2**(7), 2**(7)+1,2**(7)-1, 2**(7)-2, 2**(8)-1, 2**(8)-2,
                        0b01010101, 0b10101010, 0b01011011, 0b11011011]
      corners_32bit = [0, 1, 2, 2**(31), 2**(31)+1, 2**(31)-1, 2**(31)-2, 2**32-1, 2**32-2,
                        0b10101010101010101010101010101010, 0b01010101010101010101010101010101,
                        0b01100011101011101000011011110111, 0b11100011101011101000011011110111]
      corners_6bit = [0, 1, 2, 2**(5), 2**(5)+1, 2**(5)-1, 2**(5)-2, 2**(6)-1, 2**(6)-2,
                        0b101010, 0b010101, 0b010110]
#      corners_imm_6bit = [0, 1, 2, 31, 30, -32, -31, -2, -1]
      corners_imm_6bit = [0, 1, 2, 3, 4, 8, 16, 30, 31, -32, -31, -2, -1]
      corners_20bit = [0,0b11111111111111111111000000000000,0b10000000000000000000000000000000,
                        0b00000000000000000001000000000000,0b01001010111000100000000000000000]
      c_slli_32_corners  = [0,1,0b01000000000000000000000000000000,0b00111111111111111111111111111111,
                            0b01111111111111111111111111111111,0b01010101010101010101010101010101,
                            0b00101101110111100100010000111011]
      c_slli_64_corners  = [0x0000000000000000,0x0000000000000001,0x4000000000000000,0x0000000007fffffff,0x000000080000000,
                            0x3FFFFFFFFFFFFFFF,0x7FFFFFFFFFFFFFFF,0x5555555555555555,0x2DDE443BB1D7437B]
      c_srli_32_corners  = [0,2,4,0b11111111111111111111111111111110, 0b11111111111111111111111111111100,
                            0b10101010101010101010101010101010,0b10110111011110010001000011101110]
      c_srli_64_corners =  [0x000000000000000,0x00000000000000002,0x0000000000000004,0x00000001fffffffe,0x00000001fffffffc,
                            0x0000000200000000,0x0000000200000002,0xfffffffffffffffe,0xfffffffffffffffc,0xaaaaaaaaaaaaaaaa,
                            0xb77910eec75d0dee]
      c_srai_32_corners  = [0,2,4,0b11111111111111111111111111111110, 0b00110111011110010001000011101110]
      c_srai_64_corners  = [0x0000000000000000,0x0000000000000002,0x0000000000000004,0x00000001fffffffe,0x00000001fffffffc,
                            0x0000000200000000,0x0000000200000002,0xfffffffffffffffe,0xfffffffffffffffc,0x377910eec75d0dee]


      fcorners =            [0x00000000, # 0
                               0x80000000, # -0
                               0x3f800000, # 1.0
                               0xbf800000, # -1.0
                               0x3fc00000, # 1.5
                               0xbfc00000, # -1.5
                               0x40000000,  # 2.0
                               0xc0000000,  # -2.0 
                               0x00800000,  # smallest positive normalized
                               0x80800000,  # smallest negative normalized
                               0x7f7fffff,  # most positive
                               0xff7fffff,  # most negative
                               0x007fffff,  # largest positive subnorm
                               0x807fffff,  # largest negative subnorm
                               0x00400000,  # positive subnorm with leading 1
                               0x80400000,  # negative subnorm with leading 1
                               0x00000001,  # smallest positive subnorm
                               0x80000001,  # smallest negative subnorm
                               0x7f800000,  # positive infinity
                               0xff800000,  # negative infinity
                               0x7fc00000,  # canonical quiet NaN
                               0x7fffffff,  # noncanonical quiet NaN
                               0xffffffff,  # noncanonical quiet NaN with sign bit set
                               0x7f800001,  # signaling NaN with lsb set
                               0x7fbfffff,  # signaling NaN with all mantissa bits set
                               0xffbfffff,  # signaling Nan with all mantissa bits and sign bit set
                               0x7ef8654f,  # random positive 1.65087e+38
                               0x813d9ab0]  # random negative -3.48248e-38

      fcornersD = [0x0000000000000000, # 0.0
                  0x8000000000000000,  # -0.0
                  0x3FF0000000000000,  # 1.0
                  0xBFF0000000000000,  # -1.0
                  0x3FF8000000000000,  # 1.5
                  0xBFF8000000000000,  #-1.5
                  0x4000000000000000,  # 2.0
                  0xc000000000000000,  # -2.0
                  0x0010000000000000,  # smallest positive normalized
                  0x8010000000000000,  # smallest negative normalized
                  0x7FEFFFFFFFFFFFFF,  # most positive normalized
                  0xFFEFFFFFFFFFFFFF,  # most negative normalized
                  0x000FFFFFFFFFFFFF,  # largest positive subnorm
                  0x800FFFFFFFFFFFFF,  # largest negative subnorm
                  0x0008000000000000,  # mid positive subnorm
                  0x8008000000000000,  # mid negative subnorm
                  0x0000000000000001,  # smallest positive subnorm
                  0x8000000000000001,  # smallest negative subnorm
                  0x7FF0000000000000,  # positive infinity
                  0xFFF0000000000000,  # negative infinity
                  0x7FF8000000000000,  # canonical quiet NaN
                  0x7FFFFFFFFFFFFFFF,  # noncanonical quiet NaN
                  0xFFF8000000000000,  # noncanonical quiet NaN with sign bit set
                  0x7FF0000000000001,  # signaling NaN with lsb set
                  0x7FF7FFFFFFFFFFFF,  # signaling NaN with all mantissa bits set
                  0xFFF0000000000001,  # signaling NaN with lsb and sign bits set
                 0x5A392534A57711AD, # 4.25535e126 random positive
                  0xA6E895993737426C] # -2.97516e-121 random negative

      fcornersH = [0x0000, # 0.0
                   0x8000, # -0.0
                   0x3C00, # 1.0
                   0xBC00, # -1.0
                   0x3E00, # 1.5
                   0xBE00, # -1.5
                   0x4000, # 2.0
                   0xC000, # -2.0
                   0x0400, # smallest normalized
                   0x8400, # smallest negative normalized
                   0x7BFF, # most positive normalized
                   0xFBFF, #  most negative normalized
                   0x03FF, # largest positive subnorm
                   0x83FF,  # largest negative subnorm
                   0x0200,  # positive subnorm with leading 1
                   0x8200,  # negative subnorm with leading 1
                   0x0001, # smallest positive subnorm
                   0x8001,  # smallest negative subnorm
                   0x7C00,  # positive infinity
                   0xFC00,  # negative infinity
                   0x7E00,  # canonical quiet NaN
                   0x7FFF,  # noncanonical quiet NaN
                   0xFE00,  # noncanonical quiet NaN with sign bit set
                   0x7C01, # signaling NaN with lsb set
                   0x7DFF,  # signaling NaN with all mantissa bits set
                   0xFC01,  # signaling NaN with lsb and sign bits set
                   0x58B4,  # 150.5 random positive
                   0xC93A]  # -10.4531 random negative

      # fcornersQ = [] # TODO: Fill out quad precision F corners

      badNB_corners_D_S =  [0xffffefff00000000,
                            0xaaaaaaaa80000000,
                            0x000000003f800000,
                            0xdeadbeefbf800000,
                            0xa1b2c3d400800000,
                            0xffffffef80800000,
                            0xfeffffef7f7fffff,
                            0x7e7e7e7eff7fffff,
                            0x7fffffff7f800000,
                            0xfffffffeff800000,
                            0xfeedbee57fc00000,
                            0xffc0deff7fffffff,
                            0xfeffffff7f800001,
                            0xfffffeff7fbfffff]

      badNB_corners_D_H =  [0xffffffff00000000,
                            0xfffffffffffe8000,
                            0x7fffffffffff3C00,
                            0xfeedbee5beefBC00,
                            0xffffffefffff0400,
                            0x00000000ffff8400,
                            0xefffffffffff7BFF,
                            0xc0dec0dec0deFBFF,
                            0xa83ef1cc4f1a7C00,
                            0xffffffff0fffFC00,
                            0xfffeffffffff7E00,
                            0xffffffefffff7FFF,
                            0xa1b2c3d4e5f67C01,
                            0xfffffffcffff7DFF]

      badNB_corners_S_H =  [0x00000000,
                            0xfffe8000,
                            0x7fff3C00,
                            0xbeefBC00,
                            0xfeff0400,
                            0x0fff8400,
                            0xefff7BFF,
                            0xc0deFBFF,
                            0x4f1a7C00,
                            0x0fffFC00,
                            0xffef7E00,
                            0xfeef7FFF,
                            0xa1b27C01,
                            0x4fd77DFF]

      # global NaNBox_tests
      NaNBox_tests = False

      pathname = f"{ARCH_VERIF}/tests/rv{xlen}/{extension}/"
      cmd = "mkdir -p " + pathname + " ; rm -f " + pathname + "/*" # make directory and remove old tests in dir
      os.system(cmd)
      for test in coverpoints.keys():
        #print("Generating test for ", test, " with entries: ", coverpoints[test])

        basename = "WALLY-COV-" + test
        fname = pathname + "/" + basename + ".S"

        # print custom header part
        f = open(fname, "w")
        line = "///////////////////////////////////////////\n"
        f.write(line)
        line="// "+fname+ "\n// " + author + "\n"
        f.write(line)
        line ="// Created " + str(datetime.now()) + "\n"
        f.write(line)

        # insert generic header
        h = open(f"{ARCH_VERIF}/templates/testgen_header.S", "r")
        for line in h:
          f.write(line)

        # add assembly lines to enable fp where needed
        if test in floattypes:
          float_en = "\n# set mstatus.FS to 01 to enable fp\nli t0,0x4000\ncsrs mstatus, t0\n\n"
          f.write(float_en)

        write_tests(coverpoints[test], test, xlen)

        # print footer
        line = "\n.EQU NUMTESTS," + str(1) + "\n\n"
        f.write(line)
        h = open(f"{ARCH_VERIF}/templates/testgen_footer.S", "r")
        for line in h:
          f.write(line)

      # Finish
      f.close()