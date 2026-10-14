
import matplotlib.pyplot as plt
import numpy as np


def find_crossings(x, y, threshold):
    """Find interpolated x coordinates where y crosses threshold."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    crossings = []

    for i in range(len(x) - 1):
        y0, y1 = y[i], y[i + 1]

        if (y0 - threshold) * (y1 - threshold) < 0:
            frac = (threshold - y0) / (y1 - y0)
            crossings.append(
                x[i] + frac * (x[i + 1] - x[i])
            )
        elif y0 == threshold:
            crossings.append(x[i])

    return crossings


def insert_points(x, y, extra_x):
    """Insert extra x points and interpolate their y values."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if not extra_x:
        return x, y

    new_x = np.concatenate([x, extra_x])
    order = np.argsort(new_x)
    new_x = new_x[order]
    new_y = np.interp(new_x, x, y)

    keep = np.concatenate(([True], np.diff(new_x) > 1e-9))

    return new_x[keep], new_y[keep]


def curvegraph(
    df,
    pump_power,
    city,
    solar_peak,
    panel_quantity,
    panel_power
):
    x = list(range(len(df)))
    pv = df["photovoltaic_power"]

    crossings = find_crossings(x, pv, pump_power)

    ax, apv = insert_points(x, pv, crossings)
    top_capped = np.minimum(apv, pump_power)

    fig, plot = plt.subplots(figsize=(12, 6))

    # Photovoltaic power
    plot.plot(
        x,
        pv,
        color="royalblue",
        linewidth=3,
        marker="o",
        label="Photovoltaic Power"
    )

    # Pump rated power
    plot.axhline(
        y=pump_power,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Pump Rated Power"
    )

    if crossings:
        c_min, c_max = min(crossings), max(crossings)

        i_min = np.searchsorted(ax, c_min)
        i_max = np.searchsorted(ax, c_max)

        plot.fill_between(
            ax[:i_min + 1],
            0,
            top_capped[:i_min + 1],
            color="gold",
            alpha=0.5,
            label="Partial Operation"
        )

        plot.fill_between(
            ax[i_min:i_max + 1],
            0,
            top_capped[i_min:i_max + 1],
            color="limegreen",
            alpha=0.45,
            label="Maximum Efficiency"
        )

        plot.fill_between(
            ax[i_max:],
            0,
            top_capped[i_max:],
            color="gold",
            alpha=0.5
        )

        max_efficiency_hours = c_max - c_min

        plot.text(
            (c_min + c_max) / 2,
            pump_power * 0.5,
            f"{max_efficiency_hours:.0f} hours",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold"
        )

    else:
        plot.fill_between(
            ax,
            0,
            top_capped,
            where=apv > 0,
            interpolate=True,
            color="gold",
            alpha=0.5,
            label="Partial Operation"
        )

    # Unused energy
    plot.fill_between(
        ax,
        pump_power,
        apv,
        where=apv > pump_power,
        interpolate=True,
        color="red",
        alpha=0.35,
        label="Unused Energy"
    )

    # Crossing lines
    for xc in crossings:
        plot.vlines(
            x=xc,
            ymin=0,
            ymax=pump_power,
            color="black",
            linestyle="--",
            linewidth=2,
            alpha=0.8
        )

    if crossings:
        plot.plot(
            [],
            [],
            color="black",
            linestyle="--",
            linewidth=2,
            label="Max Efficiency Threshold"
        )

        plot.plot(
            crossings,
            [pump_power] * len(crossings),
            linestyle="None",
            marker="o",
            markersize=8,
            color="royalblue",
            markeredgecolor="black",
            markeredgewidth=1.2,
            zorder=6
        )

    # Green dots
    plot.scatter(
        [i for i in x if pv.iloc[i] >= pump_power],
        [pv.iloc[i] for i in x if pv.iloc[i] >= pump_power],
        color="green",
        s=70,
        zorder=5
    )

    # Configuration
    plot.set_xticks(x)
    plot.set_xticklabels(df["interval"], rotation=45)

    plot.set_xlabel("Hour")
    plot.set_ylabel("Power (W)")
    plot.set_title("Photovoltaic Power vs Pump Rated Power")

    fig.text(
        0.125,
        0.92,
        f"Location: {city}\n"
        f"Solar Peak Hour: {solar_peak:.2f} kWh/kWp/day\n"
        f"Panels: {panel_quantity}\n"
        f"Installed Power: {panel_power * panel_quantity} W",
        ha="left",
        va="top",
        fontsize=10
    )

    plot.grid(True, alpha=0.3)
    plot.legend()

    fig.tight_layout()

    return fig
