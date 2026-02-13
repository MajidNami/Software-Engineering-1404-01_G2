from .models import Place
from math import tanh

### 0:Single, 1:Couple, 2:Family, 3:Business, 4:Friends
styleMtx = [
#   S     C     F     B     Fr
    [1.0, 0.7,  0.4,  0.2,  0.8],  # Single
    [0.7, 1.0,  0.8,  0.3,  0.6],  # Couple
    [0.4, 0.8,  1.0,  0.3,  0.5],  # Family
    [0.2, 0.3,  0.3,  1.0,  0.4],  # Business
    [0.8, 0.6,  0.5,  0.4,  1.0],  # Friends
]


seasonMtx = [
    #  Sp     Su     Fa     Wi
    [ 1.0,   0.7,   0.5,   0.3 ],  # Spring
    [ 0.7,   1.0,   0.6,   0.4 ],  # Summer
    [ 0.5,   0.6,   1.0,   0.7 ],  # Fall
    [ 0.3,   0.4,   0.7,   1.0 ],  # Winter
]


budgetMtx = [
    #   Eco    Mod    Lux
    [ 1.0,   0.7,   0.3 ],  # Economy
    [ 0.7,   1.0,   0.6 ],  # Moderate
    [ 0.3,   0.6,   1.0 ],  # Luxury
]


styleIndex = {
    'SINGLE' : 0,
    'COUPLE' : 1,
    'FAMILY' : 2,
    'BUSINESS' : 3,
    'FRIENDS' : 4
}

seasonIndex = {
    'SPRING' : 0,
    'SUMMER' : 1,
    'FALL' : 2,
    'WINTER' : 3
}

budgetIndex = {
    'ECONOMY' : 0,
    'MODERATE' : 1,
    'LUXURY' : 2
}


def scoreByStyle(places, targetStyle):
    result = []
    ts = styleIndex[targetStyle]

    for place in places:
        style = styleIndex[place.travel_style]
        placeId = place.place_id
        score = styleMtx[ts][style]
        result.append((placeId, score))
    
    return result 



def scoreBySeason(places, targetSeason):
    result = []
    ts = seasonIndex[targetSeason]

    for place in places:
        season = seasonIndex[place.season]
        placeId = place.place_id
        score = seasonMtx[ts][season]
        result.append((placeId, score))
    
    return result 

def scoreByBudget(places, targetBudget):
    result = []
    tb = budgetIndex[targetBudget]

    for place in places:
        budget = budgetIndex[place.budget_level]
        placeId = place.place_id
        score = budgetMtx[tb][budget]
        result.append((placeId, score))
    
    return result         


def scoreByDuration(places, targetDuration):
    result = []
    
    for place in places:
        placeId = place.place_id
        deltaT = targetDuration - place.duration
        score = (tanh(deltaT) + 1)/2
        result.append((placeId, max(score, 0.01)))

    return result


    

