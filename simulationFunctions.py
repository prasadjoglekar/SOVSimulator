import pandas as pd
import numpy as np

def createSimulationSnaps(addressableImpsDF, baseDF):
    linearPrice = 1

    brandAImpsDict = {}
    brandAPriceDict = {}
    brandAKeylogDict = {}

    for addrPrice in np.arange(1, 1.4, 0.1):

        for linearImpsPerHH in range(0, 6):
            linearImpsPriceDF = baseDF[['Population']].copy()
            linearImpsPriceDF['LinearImps'] = linearImpsPriceDF['Population'] * linearImpsPerHH
            linearImpsPriceDF['LinearCost'] = linearImpsPriceDF['LinearImps'] * linearPrice / 1000
            linearImpsPriceDF

            for addrFreq in range(1, 15):
                dictKey = f'LFreq{linearImpsPerHH}_AFreq{addrFreq}_APrice{addrPrice:.2f}'

                addressabilityDFImpressionsSnap = addressableImpsDF.copy()
                addressabilityDFImpressionsSnap.update(addressabilityDFImpressionsSnap.iloc[:, 1:11 + 1].multiply(
                    addressabilityDFImpressionsSnap['Population'], 0) * addrFreq)

                addressabilityDFCostSnap = addressabilityDFImpressionsSnap.copy()
                addressabilityDFCostSnap.update(addressabilityDFCostSnap.iloc[:, 1:11 + 1] * addrPrice / 1000)

                combinedImpressionsSnap = addressabilityDFImpressionsSnap.copy()
                combinedPriceSnap = addressabilityDFCostSnap.copy()
                combinedImpressionsSnap.update(
                    combinedImpressionsSnap.iloc[:, 1:].add(linearImpsPriceDF['LinearImps'], axis=0))
                combinedPriceSnap.update(combinedPriceSnap.iloc[:, 1:].add(linearImpsPriceDF['LinearCost'], axis=0))

                brandAImpsDict[dictKey] = combinedImpressionsSnap
                brandAPriceDict[dictKey] = combinedPriceSnap
                brandAKeylogDict[dictKey] = [linearImpsPerHH, addrFreq, addrPrice]

    return [brandAImpsDict, brandAPriceDict, brandAKeylogDict]


def simulationRunner(brandAImpsDict, brandAPriceDict, brandAKeylogDict):
    # Now for each dict entry, subset to the largest "Snap" that's below budget.
    reallocateSwitch = True
    breakKey = False

    maxBudget = 630000
    iterKeys = brandAPriceDict.keys()

    brandAFinalDict = {}


    for iterKey in iterKeys:
        # pause for specific keys
        if breakKey and iterKey == 'LFreq2_AFreq14_APrice1.10':
            print("here")
        elif breakKey:
            continue

        reallocated = False

        linFreq, addrFreq, addrPrice = brandAKeylogDict[iterKey]

        priceDF = brandAPriceDict[iterKey]
        impDF = brandAImpsDict[iterKey]
        decilePopulation = impDF['Population'][0]

        optimalColumn = priceDF.iloc[:, 1:].loc[:, (priceDF.sum(axis=0) <= maxBudget)]
        # b.iloc selects the Snap Columns. .loc then selects columns that fit the <= condition.

        # print(f'Processing Key: {brandAKeylogDict[iterKey]}')

        if optimalColumn.empty:
            print(f'No Optimal Column found for key {brandAKeylogDict[iterKey]}')
            continue

        optimalColumn = optimalColumn.iloc[:, -1:].columns[0]
        # this .iloc gets the name of last (highest) column

        # if amount not used is greater than a 3rd of the budget, then this solution is clearly sub-optimal. We want to show it.
        # if it's less than a 3rd, then we want to apply the remainder proportionally to the deciles using addressable.

        deltaBudget = maxBudget - priceDF[optimalColumn].sum()

        if (deltaBudget <= 0):
            # don't reallocate
            pass
        elif (deltaBudget > 0 and (not reallocateSwitch)):
            pass
        elif (deltaBudget >= priceDF[optimalColumn].sum() * 0.49):
            pass
        else:

            # Reallocate to the deciles that don't have any addressable.
            t = priceDF[optimalColumn].tolist()
            u = impDF[optimalColumn].tolist()

            if breakKey:
                print(t)
                print(u)

            addrImps = addrFreq * decilePopulation
            linImps = linFreq * decilePopulation
            oneAddrImpMoreCost = 1 * decilePopulation * addrPrice / 1000

            for i, amount in enumerate(t):

                if u[i] <= addrImps + linImps:
                    amountToAdd = deltaBudget if oneAddrImpMoreCost > deltaBudget else oneAddrImpMoreCost
                    deltaBudget = deltaBudget - amountToAdd
                    impsToAdd = amountToAdd * 1000 / addrPrice

                    t[i] = amount + amountToAdd
                    u[i] = u[i] + impsToAdd
                    reallocated = True

            updatedPriceDF = pd.DataFrame(t, index=priceDF.index, columns=[optimalColumn])
            priceDF.update(updatedPriceDF)
            updatedPriceDF = pd.DataFrame(u, index=impDF.index, columns=[optimalColumn])
            impDF.update(updatedPriceDF)

        # print(f'Finished Processing Key: {brandAKeylogDict[iterKey]}; Reallocated {reallocated}; Money Left: {deltaBudget}')

        impDFOptimal = priceDF[['Population', optimalColumn]]
        impDFOptimal = impDFOptimal.rename(columns={optimalColumn: iterKey + '_Spend'})
        impDFOptimal[iterKey + '_Impressions'] = impDF[optimalColumn]
        brandAFinalDict[iterKey] = impDFOptimal

    return brandAFinalDict