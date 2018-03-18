import argparse
import sys
import operator
import collections
from dateutil import parser
from pprint import pprint
from prettytable import PrettyTable


class entry:
    def __init__(self):
        self.unixtime = -1
        self.user = ""

    def set(self, str):
        if "<auth.info>" in str:
            self.set_type2(str)
        else:
            self.set_type1(str)
        return

    def set_type1(self, str):
        token = str.split(" ")
        token = [x for x in token if x]
        time = parser.parse(token[0] + " " + token[1] + " " + token[2])
        self.unixtime = time.timestamp()
        self.user = token[7]

    def set_type2(self, str):
        token = str.split(" ")
        token = [x for x in token if x]
        time = parser.parse(token[0] + " " + token[1] + " " + token[2])
        self.unixtime = time.timestamp()
        self.user = token[8]


class option:
    def __init__(self):
        self.sortby = "count"
        self.after = 0
        self.before = sys.maxsize
        self.reverse = False
        self.morethan = 0
        self.top = sys.maxsize


if __name__ == "__main__":
    parsor = argparse.ArgumentParser()
    parsor.add_argument("-u", help="sort by user", action="count")
    parsor.add_argument(
        "-after", help="filter log after special date", nargs="?")
    parsor.add_argument(
        "-before", help="filter log before special date", nargs="?")
    parsor.add_argument(
        "-n", help="how only the user of most N-th times", nargs="?", type=int)
    parsor.add_argument(
        "-t",
        help="show only the user of attacking equal or more than N-th times",
        nargs="?", type=int)
    parsor.add_argument("-r", help="sort in reverse order", action="count")
    parsor.add_argument("filename", help="Log file path.", nargs="*")

    args = parsor.parse_args()
    opt = option()

    if args.u:
        opt.sortby = "user"
    if args.after:
        opt.after = parser.parse(args.after).timestamp()
    if args.before:
        opt.before = parser.parse(args.before).timestamp()
    if args.n:
        opt.top = args.n
    if args.t:
        opt.morethan = args.t
    if args.r:
        opt.reverse = True

    entries = []
    for filename in args.filename:
        f = open(filename, "r")
        for line in f:
            e = entry()
            if "Invalid user" in line:
                e.set(line)
                entries.append(e)
        f.close()

    summery = {}
    for e in entries:
        if e.unixtime > opt.after and \
           e.unixtime < opt.before:
            try:
                summery[e.user] = summery[e.user] + 1
            except KeyError:
                summery[e.user] = 1

    if opt.sortby == "count":
        sorted_summery = collections.OrderedDict(
            sorted(summery.items(), key=lambda t: -t[1], reverse=opt.reverse))
    else:
        sorted_summery = collections.OrderedDict(
            sorted(summery.items(), key=lambda t:  t[0], reverse=opt.reverse))
    x = PrettyTable()
    x.field_names = ["user", "count"]
    top = 0
    for user in sorted_summery:
        top = top + 1
        if top > opt.top:
            break
        if sorted_summery[user] > opt.morethan:
            x.add_row([user, sorted_summery[user]])

    print(x)
