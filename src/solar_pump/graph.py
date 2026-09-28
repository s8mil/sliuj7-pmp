import matplotlib.pyplot as plt
import numpy as np

def find_crossings(x, y, threshold):
    """Encuentra los puntos x (interpolados) donde y cruza threshold."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    crossings = []
    for i in range(len(x) - 1):
        y0, y1 = y[i], y[i + 1]
        if (y0 - threshold) * (y1 - threshold) < 0:
            frac = (threshold - y0) / (y1 - y0)
            crossings.append(x[i] + frac * (x[i + 1] - x[i]))
        elif y0 == threshold:
            crossings.append(x[i])
    return crossings


def insert_points(x, y, extra_x):
    """Inserta puntos extra (ej. cruces) en las series x, y, interpolando sus valores y."""
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

    plt.figure(figsize=(12, 6))

    # Photovoltaic power line
    plt.plot(
        x,
        pv,
        color="royalblue",
        linewidth=3,
        marker="o",
        label="Photovoltaic Power"
    )

    # Pump rated power line
    plt.axhline(
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

        plt.fill_between(
            ax[:i_min + 1],
            0,
            top_capped[:i_min + 1],
            color="gold",
            alpha=0.5,
            label="Partial Operation"
        )

        plt.fill_between(
            ax[i_min:i_max + 1],
            0,
            top_capped[i_min:i_max + 1],
            color="limegreen",
            alpha=0.45,
            label="Maximum Efficiency"
        )

        plt.fill_between(
            ax[i_max:],
            0,
            top_capped[i_max:],
            color="gold",
            alpha=0.5
        )

        max_efficiency_hours = c_max - c_min

        plt.text(
            (c_min + c_max) / 2,
            pump_power * 0.5,
            f"{max_efficiency_hours:.0f} hours",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold"
    )
    else:
        plt.fill_between(
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
    plt.fill_between(
        ax,
        pump_power,
        apv,
        where=apv > pump_power,
        interpolate=True,
        color="red",
        alpha=0.35,
        label="Unused Energy"
    )

    # Líneas verticales en los cruces
    for xc in crossings:
        plt.vlines(
            x=xc,
            ymin=0,
            ymax=pump_power,
            color="black",
            linestyle="--",
            linewidth=2,
            alpha=0.8
        )

    if crossings:
        plt.plot(
            [],
            [],
            color="black",
            linestyle="--",
            linewidth=2,
            label="Max Efficiency Threshold"
        )

    # Puntos de intersección
    if crossings:
        plt.plot(
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

    plt.figtext(
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

    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()
