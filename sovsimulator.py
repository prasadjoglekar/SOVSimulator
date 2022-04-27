import pandas as pd
import simulationFunctions as sf
import plotFunctions as pf

liftDicts = {
    "moderateModelLift":[2.00,1.80,1.50,1.20,1.00,0.80,0.65,0.55,0.30,0.20],
    "highModelLift":[3.00,2.00,1.50,1.20,0.90,0.50,0.40,0.30,0.15,0.05]
}

purchaseDicts = {
    "sparsePurchase" : [250000,250000,250000,250000,250000,250000,250000,250000,250000,250000],
    "moderatePurchase" : [500000,500000,500000,500000,500000,500000,500000,500000,500000,500000],
    "densePurchase" : [1000000,1000000,1000000,1000000,1000000,1000000,1000000,1000000,1000000,1000000]
}



def readData(lift, purchase):

    df = pd.read_csv('data.tsv', sep='\t')
    df.index = df.iloc[:, 0]
    df = df.drop(df.columns[0], axis=1)
    df.index.names = [None]

    df["Model Lift"] = lift
    df["Buyers / Q"] = purchase

    return df


def createAddressableSnapDF(baseDF):
    
    addressableImpsDF = baseDF[['Population']].copy()
    
    for i in range (0, 11):
        col = [0] * 10
        for j in range (0, 10):
            if j >= i:
                col[j] = 0
            else:
                col[j] = 1
        tempdf = pd.DataFrame(col, index=df.index, columns=["Snap " + str(i + 1)])
        addressableImpsDF = pd.concat([addressableImpsDF, tempdf], axis=1)

    return addressableImpsDF


def createBaseDF(df):
    
    ImpsPerHH = 5
    ImpsSeries = [ImpsPerHH] * 10
    ImpsSeries = pd.DataFrame(ImpsSeries, index=df.index, columns=["Imps Per HH"])
    
    MediaCPM = 1
    CPMSeries = [MediaCPM] * 10
    CPMSeries = pd.DataFrame(CPMSeries, index=df.index, columns=["Full Footprint CPM"])
    
    tempdf = pd.concat([ImpsSeries, CPMSeries], axis=1)
    
    Brands = ['Brand A', 'Brand B', 'Brand C']
    ShareOfMktPerBrand = 1 / len(Brands)
    
    for brand in Brands:
        brandSeries = [ShareOfMktPerBrand] * 10
        brandSeries = pd.DataFrame(brandSeries, index=df.index, columns=[brand + " Base Share of Market"])
        tempdf = pd.concat([tempdf, brandSeries], axis=1)
    
    df = pd.concat([df, tempdf], axis=1)
    
    df['Brand A Base Share of Voice'] = df['Brand A Base Share of Market']
    df['Brand B Base Share of Voice'] = df['Brand B Base Share of Market']
    df['Brand C Base Share of Voice'] = df['Brand C Base Share of Market']
    
    df['Brand A Base Share of Spend'] = df['Brand A Base Share of Market']
    df['Brand B Base Share of Spend'] = df['Brand B Base Share of Market']
    df['Brand C Base Share of Spend'] = df['Brand C Base Share of Market']
    
    return df


def computeShareMetrics(baseDF, brandAFinalDict):
    Q0DF = baseDF[['Population']].copy()
    Q0DF['Modeled Buyers in Decile'] = baseDF['Model Lift'] * baseDF['Buyers / Q']
    Q0DF['Modeled Non-Buyers in Decile'] = Q0DF['Population'] - Q0DF['Modeled Buyers in Decile']

    Q0DF['Brand A Impressions'] = baseDF['Population'] * baseDF['Imps Per HH']
    Q0DF['Brand B Impressions'] = Q0DF['Brand A Impressions']
    Q0DF['Brand C Impressions'] = Q0DF['Brand A Impressions']

    Q0DF['Brand A Cost'] = Q0DF['Brand A Impressions'] / 1000 * baseDF['Full Footprint CPM']
    Q0DF['Brand B Cost'] = Q0DF['Brand A Cost']
    Q0DF['Brand C Cost'] = Q0DF['Brand A Cost']

    iterKeys = brandAFinalDict.keys()
    brandAQ0SnapDict = {}

    shareDF = pd.DataFrame(columns=['LinFreq', 'AddrFreq', 'AddrPrice', 'ShareOfVoice', 'IndexKey'])



    for iterKey in iterKeys:
        Q0DFSnap = Q0DF.iloc[:, [0, 1, 2, 4, 5, 7, 8]]
        Q0DFSnap = pd.concat([Q0DFSnap, brandAFinalDict[iterKey].iloc[:, [1, 2]]], axis=1)
        Q0DFSnap['TotalMarketImps'] = Q0DFSnap.iloc[:, [3, 4, 8]].sum(axis=1)
        Q0DFSnap['TotalMarketSpend'] = Q0DFSnap.iloc[:, [5, 6, 7]].sum(axis=1)

        Q0DFSnap['BrandAShareOfVoice'] = Q0DFSnap.iloc[:, 8] / Q0DFSnap['TotalMarketImps']
        Q0DFSnap['BrandAShareOfSpend'] = Q0DFSnap.iloc[:, 7] / Q0DFSnap['TotalMarketSpend']

        Q0DFSnap['BrandBShareOfVoice'] = Q0DFSnap.iloc[:, 3] / Q0DFSnap['TotalMarketImps']
        Q0DFSnap['BrandBShareOfSpend'] = Q0DFSnap.iloc[:, 5] / Q0DFSnap['TotalMarketSpend']

        Q0DFSnap['BrandCShareOfVoice'] = Q0DFSnap.iloc[:, 4] / Q0DFSnap['TotalMarketImps']
        Q0DFSnap['BrandCShareOfSpend'] = Q0DFSnap.iloc[:, 6] / Q0DFSnap['TotalMarketSpend']

        Q0DFSnap['BrandASales'] = Q0DFSnap['BrandAShareOfVoice'] * Q0DFSnap.iloc[:, 1]
        Q0DFSnap['BrandBSales'] = Q0DFSnap['BrandBShareOfVoice'] * Q0DFSnap.iloc[:, 1]
        Q0DFSnap['BrandCSales'] = Q0DFSnap['BrandCShareOfVoice'] * Q0DFSnap.iloc[:, 1]

        brandAQ0SnapDict[iterKey] = Q0DFSnap

        linFreq = brandAKeylogDict[iterKey][0]
        addrFreq = brandAKeylogDict[iterKey][1]
        addrPrice = brandAKeylogDict[iterKey][2]
        share = Q0DFSnap['BrandASales'].sum() / Q0DFSnap['Modeled Buyers in Decile'].sum()

        shareDF = shareDF.append(
            {'LinFreq': linFreq, 'AddrFreq': addrFreq, 'AddrPrice': addrPrice, 'ShareOfVoice': share, 'IndexKey': iterKey},
            ignore_index = True)

    #Get max share index
    maxShareIdx = shareDF.groupby(['LinFreq', 'AddrPrice'])['ShareOfVoice'].idxmax()

    bestSolutionDF = pd.DataFrame()


    for index, items in maxShareIdx.items():
        bestSolutionKey = shareDF.iloc[[(maxShareIdx[index])]]['IndexKey'].iloc[0]
        #bestSolutionDict[bestSolutionKey] = brandAQ0SnapDict[bestSolutionKey]
        tempDF = brandAQ0SnapDict[bestSolutionKey].iloc[:, 11:13].copy()
        tempDF.rename(columns = {'BrandAShareOfVoice':f'{bestSolutionKey}_SOV', 'BrandAShareOfSpend':f'{bestSolutionKey}_SOS'}, inplace = True)
        bestSolutionDF = pd.concat([bestSolutionDF, tempDF], axis=1)

    return [shareDF, brandAQ0SnapDict, bestSolutionDF]



if __name__ == "__main__":

    combinedShares = []
    for liftKey in liftDicts:
        for purchKey in  purchaseDicts:

            shareFileName = f'share_{liftKey}_{purchKey}.csv'
            bestSolFileName = f'bestSolution_{liftKey}_{purchKey}.csv'

            df = readData(liftDicts[liftKey],purchaseDicts[purchKey])
            baseDF = createBaseDF(df)
            addressableImpsDF = createAddressableSnapDF(baseDF)
            brandAImpsDict, brandAPriceDict, brandAKeylogDict = sf.createSimulationSnaps(addressableImpsDF, baseDF)
            brandAFinalDict = sf.simulationRunner(brandAImpsDict, brandAPriceDict, brandAKeylogDict)
            shareDF, brandAQ0SnapDict, bestSolutionDF = computeShareMetrics(baseDF, brandAFinalDict)

            shareDF['Lift'] = liftDicts[liftKey][0]
            shareDF['Purchasers'] = purchaseDicts[purchKey][0]
            shareDF.to_csv(shareFileName)
            bestSolutionDF.to_csv(bestSolFileName)
            combinedShares.append(shareDF)

    t = pd.concat(combinedShares)
    t.to_csv("combinedShares.csv")