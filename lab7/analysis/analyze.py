import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv(sys.argv[1])
def col(*keys):
    for c in df.columns:
        n = str(c).lower()
        if all(k in n for k in keys):
            return c
    return None

tcol = df.columns[0]
try:
    t = pd.to_numeric(df[tcol])
    t = (t - t.iloc[0])
    if t.max() > 1e5:
        t = t / 1000.0
except Exception:
    t = (pd.to_datetime(df[tcol]) - pd.to_datetime(df[tcol]).iloc[0]).dt.total_seconds()

alt = col("alt", "rel") or col("altitude")
gs = col("ground")
asp = col("air")
roll = col("roll")
lat, lon = col("lat"), col("lon")
mode, arm = col("mode"), col("arm")

a = df[alt].astype(float)
amax = a.max()
t_start = t[a > 1.0].iloc[0]
t_top = t[a >= 0.95 * amax].iloc[0]
t_land_begin = t[a >= 0.95 * amax].iloc[-1]
t_end = t[a > 0.5].iloc[-1]

print("--- Таблиця 7.4 ---")
print(f"Час зльоту: {t_top - t_start:.1f} с")
print(f"Найбільша висота: {amax:.1f} м")
if gs: print(f"Найбільша наземна швидкість: {df[gs].astype(float).max():.2f} м/с")
if asp: print(f"Найбільша повітряна швидкість: {df[asp].astype(float).max():.2f} м/с")
print(f"Час польоту: {t_end - t_start:.1f} с")
if lat and lon:
    print("Початкова координата:", df[lat].iloc[0], df[lon].iloc[0])
    print("Кінцева координата:", df[lat].iloc[-1], df[lon].iloc[-1])

def plot(y, name, ylabel, fname):
    plt.figure(figsize=(9, 4))
    plt.plot(t, df[y].astype(float))
    plt.axvspan(t_start, t_top, alpha=0.15, label="Зліт")
    plt.axvspan(t_top, t_land_begin, alpha=0.15, color="green", label="Горизонтальний політ")
    plt.axvspan(t_land_begin, t_end, alpha=0.15, color="red", label="Посадка")
    plt.xlabel("Час, с"); plt.ylabel(ylabel); plt.title(name)
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.savefig(fname, dpi=150); plt.close()

plot(alt, "Висота від часу", "Висота, м", "graph_altitude.png")
if asp: plot(asp, "Повітряна швидкість від часу", "м/с", "graph_airspeed.png")
if gs: plot(gs, "Наземна швидкість від часу", "м/с", "graph_groundspeed.png")
print("Графіки збережено в: ~/fpv_labs/lab7/analysis/")
