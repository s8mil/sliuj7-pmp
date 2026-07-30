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


def curvegraph(df, pump_power, city, solar_peak):

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

        # Índices exactos de los puntos de cruce dentro del arreglo aumentado
        i_min = np.searchsorted(ax, c_min)
        i_max = np.searchsorted(ax, c_max)

        # --- Tramo izquierdo (amarillo): desde el inicio hasta el primer cruce ---
        plt.fill_between(
            ax[:i_min + 1],
            0,
            top_capped[:i_min + 1],
            color="gold",
            alpha=0.5,
            label="Partial Operation"
        )

        # --- Tramo central (verde): entre los dos cruces ---
        plt.fill_between(
            ax[i_min:i_max + 1],
            0,
            top_capped[i_min:i_max + 1],
            color="limegreen",
            alpha=0.45,
            label="Maximum Efficiency"
        )

        # --- Tramo derecho (amarillo): desde el segundo cruce hasta el final ---
        plt.fill_between(
            ax[i_max:],
            0,
            top_capped[i_max:],
            color="gold",
            alpha=0.5
        )
    else:
        # Caso borde: la curva nunca alcanza pump_power -> todo es amarillo
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

    # --- Unused energy: rojo donde pv > pump_power ---
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

    # --- Líneas verticales negras justo donde pv cruza pump_power ---
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
    # Entrada única en la leyenda para el umbral
    if crossings:
        plt.plot([], [], color="black", linestyle="--", linewidth=2, label="Max Efficiency Threshold")

    # --- Puntos de intersección: círculos del mismo tamaño que los de la línea pv (sin leyenda) ---
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

    # Green dots for hours where photovoltaic power is greater than or equal to pump power
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
        0.125, 0.92,
        f"Location: {city}\nSolar Peak Hour: {solar_peak:.2f} kWh/kWp/day",
        ha="left",
        va="top",
        fontsize=10
    )

    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()