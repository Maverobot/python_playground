#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt


def main():
    pd.set_option('display.width', 200)

    df = pd.read_csv("./temperature_log.csv")
    df = df.sort_values('time', ascending=True)

    arbeitszimmer_df = df.loc[df['room'].isin(['Arbeitszimmer'])]
    plt.scatter(arbeitszimmer_df['time'].tolist(),
                arbeitszimmer_df['current_temperature'])
    plt.xticks(rotation='vertical')
    plt.show()


if __name__ == "__main__":
    main()
