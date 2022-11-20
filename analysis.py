from analyzers import StaticAnalyzers
from formulas import cumulative_average, angr_weight
import math
from scraper import FundamentalAnalysis, fundamentalScrapers
from functools import reduce
from operator import concat

# simple flatten list function
def flatten(lst):
    return reduce(concat, lst)

'''
    combine_analysis: [FundamentalAnalysis] => FundamentalAnalysis
    input: a list of FundamentalAnalysis, lst
    output: a average of FundamentalAnalysis
'''
def combine_analysis(lst: list):
    if lst == []:
        return FundamentalAnalysis("NO DATA", StaticAnalyzers[16], 0, 0, 0)
    weight = list(map(lambda i: math.log(i.numAnalyzers + math.e) / (i.relevency + 1), lst))
    grade = cumulative_average(weight, list(map(lambda i: i.grade, lst)))
    num_analysts = cumulative_average(weight, list(map(lambda i: i.numAnalyzers, lst)))
    relevency = cumulative_average(weight, list(map(lambda i: i.relevency, lst)))
    return FundamentalAnalysis(lst[0].ticker, lst[0].analyzer, grade, int(num_analysts), relevency)

'''
    wipe_invalid_analysis: [FundamentalAnalysis] => [FundamentalAnalysis]
    input: a list of FundamentalAnalysis, lst
    output: lst without invalid FundamentaLAnalysis (negative values/0 analysts)
'''
def wipe_invalid_analysis(lst: list):
    return list(filter(lambda x: x.numAnalyzers > 0 and x.relevency >= 0 and x.grade > 0, lst))

'''
    deriveWeights: [FundamentalAnalysis] => [num]
    input: a list of FundamentalAnalysis, lst
    output: a list of weights from ANGR formula for each FundamentalAnalysis
'''
def deriveWeights(lst: list):
    # map each FundamentalAnalysis into ANGR weight formula
    return list(map(lambda x: angr_weight(x.analyzer.accuracy, x.numAnalyzers, x.analyzer.ranking, x.relevency), lst))
'''
    deriveGrades: [FundamentalAnalysis] => [num]
    input: a list of FundamentalAnalysis, lst
    output: a list of grades for each of lst
'''
def deriveGrades(lst: list):
    # map each FundamentalAnalysis for its grade
    return list(map(lambda x: x.grade, lst))

'''
    deriveFunamentals: string => [FundamentalAnalysis]
    input: a string, ticker that represents a ticker
    output: an array of FundamentalAnalysis types from all online gradings
'''
async def deriveFunamentals(ticker: str, reply):
    # maps ticker to each scraper and lists the outputted data
    fundamentals = []
    l = len(fundamentalScrapers)
    sources = 0
    for i, n in enumerate(fundamentalScrapers):
        alof = n(ticker)
        if len(alof) > 0:
            sources += 1
        fundamentals.append(alof)
        await reply.edit(content="*Fetching a response for " + ticker + "... " + str(int(((i + 1)/l) * 100)) + "%* (" + str(sources) + ")")
    # removes any invalid analysis due to missing data
    fundamentals = list(map(wipe_invalid_analysis, fundamentals))
    # combines analysis per site if they have multiple analysis ranges
    #   combine_analysis weights relevancy
    fundamentals = list(map(combine_analysis, fundamentals))
    total_analyzers = 0
    for i in fundamentals:
        total_analyzers += i.numAnalyzers
    return (fundamentals, int(total_analyzers))

'''
    fundamentalAverage: string => [FundamentalAnalysis]
    input: a string, ticker that represents a ticker
    output: the hegman fundamental average grade for a ticker
'''
async def fundamentalAverage(ticker: str, reply):
    ticker = ticker.upper()
    (fundamentals, ta) = await deriveFunamentals(ticker, reply)
    weights = deriveWeights(fundamentals)
    grades = deriveGrades(fundamentals)
    raw_score = cumulative_average(weights, grades)
    # catch for invalid raw scores
    if raw_score < 1 or raw_score > 5:
        return (-1, -1)
    return (round(raw_score, 3), ta)