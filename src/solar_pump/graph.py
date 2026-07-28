import matplotlib.pyplot as plt

def curvegraph(df, pump_power):

    partial_power = pump_power * 0.6

    x = range(len(df))
    pv = df["photovoltaic_power"]

    plt.figure(figsize=(12, 6))

    #Photovoltaic power line
    plt.plot(
        x,
        pv,
        color="royalblue",
        linewidth=3,
        marker="o",
        label="Photovoltaic Power"
    )

    #Pump rated power line
    plt.axhline(
        y=pump_power,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Pump Rated Power"
    )

    #Partial efficiency line at 60% of pump power
    plt.axhline(
        y=partial_power,
        color="darkorange",
        linestyle="--",
        linewidth=2,
        label="Partial Efficiency"
    )

    #Yellow area: Where photovoltaic power is greater than 0 and less than partial power
    yellow = (
        (pv > 0) &
        (pv < partial_power)
    )

    plt.fill_between(
        x,
        0,
        pv,
        where=yellow,
        interpolate=True,
        color="gold",
        alpha=0.5,
        label="Partial Operation"
    )

    #Green area: Where photovoltaic power is between partial and pump power
    green = (
        (pv >= partial_power) &
        (pv <= pump_power)
    )

    plt.fill_between(
        x,
        partial_power,
        pv,
        where=green,
        interpolate=True,
        color="limegreen",
        alpha=0.45,
        label="Maximum Efficiency"
    )

    #Unused energy: Red area where photovoltaic power is greater than pump power
    red = pv > pump_power

    plt.fill_between(
        x,
        pump_power,
        pv,
        where=red,
        interpolate=True,
        color="red",
        alpha=0.35,
        label="Unused Energy"
    )

    #Green dots for hours where photovoltaic power is greater than or equal to pump power
    plt.scatter(
        [i for i in x if pv.iloc[i] >= pump_power],
        [pv.iloc[i] for i in x if pv.iloc[i] >= pump_power],
        color="green",
        s=70,
        zorder=5
    )

    # Config
    plt.xticks(x, df["interval"], rotation=45)

    plt.xlabel("Hour")
    plt.ylabel("Power (W)")
    plt.title("Photovoltaic Power vs Pump Rated Power")

    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()