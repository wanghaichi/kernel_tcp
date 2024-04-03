import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def draw_box_chart_single(keys, values, title):
    # Create a figure and axis
    fig, ax = plt.subplots()
    # Create the boxplot
    ax.boxplot(values)
    # Set x-axis tick labels
    ax.set_xticklabels(keys, rotation=10)
    # Set y-axis label
    ax.set_ylabel('APFD')
    # Set chart title
    ax.set_title(title)
    # Show the plot
    plt.show()


def draw_box_chart_4(values, titles, x_ticks):
    assert len(values) == len(titles) == len(x_ticks) == 4
    # Create a figure and subplots
    fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(20, 4))

    for i in range(4):
        # Plot the box charts on the subplots
        axes[i].boxplot(values[i])
        axes[i].set_title(titles[i], fontsize=16)
        axes[i].set_xticklabels(x_ticks[i], rotation=10)
    for ax in axes.flat:
        ax.tick_params(axis='x', labelsize=16)
        ax.tick_params(axis='y', labelsize=16)

    # Adjust spacing between subplots
    plt.tight_layout()
    # Show the combined plot
    plt.show()


def draw_histogram(values, labels):
    a = values[0]
    b = values[1]
    # c = values[2]
    # Create labels for each rectangle
    # labels = ['a-{}'.format(i + 1) for i in range(len(a))] + ['b-{}'.format(i + 1) for i in range(len(b))]

    # Create a list of x-coordinates for each rectangle
    x = np.arange(len(labels))

    # Create a list of heights for each rectangle
    heights = a + b

    # Create a list of colors for each rectangle
    colors = ['green'] * len(a) + ['blue'] * len(b)

    # Plot the histogram
    fig, ax = plt.subplots()
    ax.bar(x, heights, tick_label=labels, color=colors)

    # Set labels and title
    ax.set_ylabel('Value')
    ax.set_xlabel('Approach')
    ax.set_title('Variance of each approach')
    plt.xticks(rotation=15)
    plt.show()


if __name__ == "__main__":
    sheets = ["history-0"]
    sheets += ["IR-0"]
    all_values = []
    all_keys = ["FC", "T-last-F", "FR", "EXD", "ROC", "T-last-E", "TfIdfModel", "LSIModel", "LDAModel", "Bm25Model"]
    for s in sheets:
        df = pd.read_excel('kernelTCP_exp_res.xlsx', sheet_name=s)
        keys = []
        values = []
        tick = []
        for c in df.columns:
            if c == "version":
                continue
            keys.append(c)
            v = df[c].tolist()[:-1]
            v = np.array(v)
            values.append(np.var(v))
        all_values.append(values)
        # all_keys.append(keys)
    print(all_values)
    draw_histogram(all_values, all_keys)
    # sheets = ["history-0", "IR-0"]
    # # sheets = ["IR-0", "IR-5", "IR-10", "IR-15"]
    # all_values = []
    # labels = ["FC", "T-last-F", "FR", "EXD", "ROC", "T-last-E", "TfIdfModel", "LSIModel", "LDAModel", "Bm25Model",
    #           "ncd", "ED", "EUD", "MHD"]
    # for s in sheets:
    #     df = pd.read_excel('kernelTCP_exp_res.xlsx', sheet_name=s)
    #     avg = df.tail(1)
    #     all_values.append(avg.values.tolist()[0][1:])
    #
    # sim_data = [0.8165124249933529, 0.8342058450140015, 0.8372497381428772, 0.8147006065895215]
    # all_values.append(sim_data)
    #
    # draw_histogram(all_values, labels)

    #
    # # Define the data
    # a = [0.5, 0.6, 0.7, 0.8]
    # b = [0.8, 0.85, 0.81, 0.99, 0.82, 0.86]
    #
    # # Define the labels for each group
    # labels = ['a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'b4']
    #
    # # Create an array of indices to represent the x-axis positions
    # x = np.arange(len(labels))
    #
    # # Combine the "a" and "b" data
    # combined_data = a + b
    #
    # # Create the histogram
    # plt.bar(x, combined_data, width=0.4, align='center', alpha=0.5)
    #
    # # Add labels and title
    # plt.xlabel('Labels')
    # plt.ylabel('Values')
    # plt.title('Histogram of a and b')
    #
    # # Set the x-axis tick positions and labels
    # plt.xticks(x, labels)
    #
    # # Show the histogram
    # plt.show()

    # sheets = ["history-0", "history-5", "history-10", "history-15"]
    # # sheets = ["IR-0", "IR-5", "IR-10", "IR-15"]
    # all_values = []
    # all_keys = []
    # for s in sheets:
    #     df = pd.read_excel('kernelTCP_exp_res.xlsx', sheet_name=s)
    #     keys = []
    #     values = []
    #     tick = []
    #     for c in df.columns:
    #         if c == "version":
    #             continue
    #         keys.append(c)
    #         values.append(df[c].tolist()[:-1])
    #     all_values.append(values)
    #     # all_keys.append(keys)
    #     all_keys.append(["FC", "T-last-F", "FR", "EXD", "ROC", "T-last-E"])
    # draw_box_chart_4(all_values, sheets, all_keys)
