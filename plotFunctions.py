import matplotlib.pyplot as plt
import pandas as pd

def plotLineCharts(shareDF, linFreq):

    plt.close("all")

    fig = plt.figure()
    labelTexts = []

    for addrPrice in shareDF.AddrPrice.unique():
        t = shareDF.loc[(shareDF['LinFreq'] == linFreq) & (shareDF['AddrPrice'] == addrPrice)]
        plt.plot(t['AddrFreq'], t['ShareOfVoice'])
        labelTexts.append(f'Addr Price: {addrPrice:.2f}')

    plt.legend(labelTexts)
    plt.xlabel("Addressable Frequency")
    plt.ylabel("Share of Voice")
    plt.axhline(y=0.33, color='black', linestyle='dashed')
    plt.show()

def plotMultiChart(shareDF):
    plt.close("all")
    labelTexts = []

    #numPrices =

    for addrPrice in shareDF.AddrPrice.unique():
        t = shareDF.loc[(shareDF['LinFreq'] == linFreq) & (shareDF['AddrPrice'] == addrPrice)]
        plt.plot(t['AddrFreq'], t['ShareOfVoice'])
        labelTexts.append(f'Addr Price: {addrPrice:.2f}')

    plt.legend(labelTexts)
    plt.xlabel("Addressable Frequency")
    plt.ylabel("Share of Voice")
    plt.axhline(y=0.33, color='black', linestyle='dashed')
    plt.show()


    fig, axs = plt.subplots(2)
    fig.suptitle('Vertically stacked subplots')
    axs[0].plot(x, y)
    axs[1].plot(x, -y)

x

if __name__ == "__main__":
    shareDF =  pd.read_csv('share.csv', sep=',')
    #plotLineCharts(shareDF, 2)
    #plotMultiChart(shareDF, 1)