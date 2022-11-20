import math
'''
ANGR Weight (W) Formula for analyzer
    angr_weight: (num, num, num, num) => num
    Input:
        a: accuracy of analyzer
            ^ a is normalized
        n: number of analysts of analyzer
        g: analyzer google ranking
        r: months since analysis
    Output: 
        weight for an analyzer
'''
def angr_weight(a, n, g, r):
    return (credibility(a, g) * math.log(n + math.e)) / (r + 1)
    
'''
Credibility (C) Formula for analyzer
    credibility: (num, num) => num
    Input:
        a: accuracy of analyzer
        g: analyzer google ranking
    Output: 
        credibility of an analyzer
'''
def credibility(a, g):
    return a / math.log(g + math.e)

'''
Normalization (N) Formula
    normalize: (num, num, num) => num
    Input:
        3 numbers, n, a maxinimum, max, a minimum min
    Output: 
        normalized value num
'''
def normalize(n, min , max):
    return (n - min)/(max - min)

'''
    normalize_list: [num] => [num]
    Input:
        a num list, alon
    Output: 
        a num list corresponding to alon's num's normalized values
'''
def normalize_list(alon):
    listMin = min(alon)
    listMax = max(alon)
    return list(map(lambda n: normalize(n, listMin, listMax), alon))

'''
    cumulative_average: ([num], [num]) => [num]
    Input:
        a num list representing weights, alow
        a num list representing ratings, alor
        the first value in weights corresponds to the first value in ratings
    Output: 
'''
def cumulative_average(alow, alor):
    sum_weight = 0
    sum_weight_rating = 0
    for weight, rating in zip(alow, alor):
        sum_weight += weight
        sum_weight_rating += weight * rating
    if sum_weight > 0:
        return sum_weight_rating / sum_weight
    return 0