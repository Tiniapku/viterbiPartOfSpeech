from collections import defaultdict, Counter
#import numpy as np
import sys
import re

class solution(object):
    def __init__(self):
        self.word = set() # word set
        self.states = set() # tag set
        self.initial_prob = Counter() # length = tag list
        self.trans_prob = defaultdict(Counter) # length = tag_list * tag_list
        self.emit_prob = defaultdict(Counter) # length = tag_list * {}
        self.frequency = defaultdict(Counter) # word: tag: frequency
        self.res = []

    def viterbi(self, obs):
        V = [{}]
        for st in self.states:
            V[0][st] = {"prob": self.initial_prob[st] * self.emit_prob[st][obs[0]], "prev": "BOS"}

        for t in range(1, len(obs)):
            V.append({})
            for st in self.states:
                max_tr_prob = max(V[t - 1][prev_st]["prob"] * self.trans_prob[prev_st][st] for prev_st in self.states)
                for prev_st in self.states:
                    if V[t - 1][prev_st]["prob"] * self.trans_prob[prev_st][st] == max_tr_prob:
                        max_prob = max_tr_prob * self.emit_prob[st][obs[t]]
                        V[t][st] = {"prob": max_prob, "prev": prev_st}
                        break
        opt = []
        max_prob = max(value["prob"] for value in V[-1].values())
        previous = "BOS"
        for st, data in V[-1].items():
            if data["prob"] == max_prob:
                opt.append(st)
                previous = st
                break
        for t in range(len(V) - 2, -1, -1):
            opt.insert(0, V[t + 1][previous]["prev"])
            previous = V[t + 1][previous]["prev"]
        self.res += opt

    def test(self, fileName):
        golden = []
        most_freq = []
        with open(fileName, 'r') as testFile:
            for line in testFile.readlines():
                line = line.strip().split(" ")
                obs = []
                result = []
                for entry in line:
                    entry = entry.replace("\/", "")
                    entry = entry.replace("*", "")
                    if entry.find('/') == -1:
                        word = entry[:-2]
                        tag = entry[-2:]
                    elif entry.count("/") == 2:
                        if "-" in entry:
                            e1, entry = entry.split("-")
                        elif "&" in entry:
                            e1, entry = entry.split("&")
                        else:
                            continue
                        w, t = e1.split("/")
                        obs.append(w)
                        result.append(t)
                    word, tag = entry.split("/")
                    obs.append(word)
                    result.append(tag)
                    if word in self.frequency:
                        most_freq.append(self.frequency[word].most_common(1)[0][0])
                    else:
                        most_freq.append(self.initial_prob.most_common(1)[0][0])
                self.viterbi(obs)
                golden += result
        count_viterbi = 0
        count_freq = 0
        for i in xrange(len(self.res)):
            if self.res[i] == golden[i]:
                count_viterbi += 1
            if most_freq[i] == golden[i]:
                count_freq += 1
        #print "golden result: ", golden
        #print "viterb result: ", self.res
        #print "freque result: ", most_freq
        print "The accuracy of viterbi algorithm is ", count_viterbi * 1.0 / len(self.res)
        print "The accuracy of frequency is ", count_freq * 1.0 / len(self.res)


    def count(self, fileName):
        self.word.add("BOS")
        self.states.add("BOS")
        with open(fileName, 'r') as inputFile:
            for line in inputFile.readlines():
                line = line.strip().split(" ")
                pre_tag = "BOS"
                for entry in line:
                    entry = entry.replace("\/", "")
                    entry = entry.replace("*","")
                    if entry.find('/') == -1:
                        word = entry[:-2]
                        tag = entry[-2:]
                    elif entry.count("/") == 2:
                        if "-" in entry:
                            e1, entry = entry.split("-")
                        elif "&" in entry:
                            e1, entry = entry.split("&")
                        else:
                            continue
                        w, t = e1.split("/")
                        self.word.add(w)
                        self.states.add(t)
                        self.initial_prob[t] += 1
                        self.trans_prob[pre_tag][t] += 1
                        self.emit_prob[t][w] += 1
                        self.frequency[w][t] += 1
                        pre_tag = t
                    else:
                        word, tag = entry.split("/")
                    self.word.add(word)
                    self.states.add(tag)
                    self.initial_prob[tag] += 1
                    self.trans_prob[pre_tag][tag] += 1
                    self.emit_prob[tag][word] += 1
                    self.frequency[word][tag] += 1
                    pre_tag = tag

        self.tag_count = len(self.states)

        for k in self.initial_prob.keys():
            self.initial_prob[k] /= self.tag_count * 1.0

        for k in self.trans_prob.keys():
            di = self.trans_prob[k]
            s = sum(di.values())
            for key in di.keys():
                di[key] /= s * 1.0
            self.trans_prob[k] = di

        for k in self.emit_prob.keys():
            di = self.emit_prob[k]
            s = sum(di.values())
            for key in di.keys():
                di[k] /= s * 1.0
            self.emit_prob[k] = di

if __name__ == "__main__":
    trainFile = sys.argv[1]
    testFile = sys.argv[2]
    s = solution()
    s.count(trainFile)
    s.test(testFile)
