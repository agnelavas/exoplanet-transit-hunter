import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.constants import R_sun, R_earth

target = "Kepler-10"
print(f"1. Fetching Kepler Quarter 3 observations for {target}...")

search_result = lk.search_lightcurve(target, mission="Kepler", quarter=3)
lc = search_result[0].download().remove_nans()

print("2. Flattening light curve to remove stellar noise...")
flat_lc = lc.flatten(window_length=101)

print("3. Running Box Least Squares (BLS) periodogram search...")
period_grid = np.linspace(0.80, 0.88, 10000)
bls = flat_lc.to_periodogram(method="bls", period=period_grid, duration=np.linspace(0.05, 0.15, 10))

best_period = bls.period_at_max_power
transit_time = bls.transit_time_at_max_power
duration = bls.duration_at_max_power
depth = bls.depth_at_max_power

print(f"\n================ RESULTS ================")
print(f"Target Planet           : Kepler-10b")
print(f"Detected Orbital Period : {best_period.value:.5f} days (~{best_period.value * 24:.1f} hours)")
print(f"Detected Transit Depth  : {depth.value:.6f}")
print(f"Transit Duration        : {duration.value * 24:.2f} hours")

# Physical radius calculation: R_p = R_star * sqrt(depth)
r_star_solar = 1.065
delta = depth.value
r_planet_solar = np.sqrt(delta) * r_star_solar
r_planet_earth = (r_planet_solar * R_sun / R_earth).decompose().value

print(f"Derived Planet Radius   : {r_planet_earth:.2f} Earth Radii")
print(f"=========================================\n")

print("4. Generating phase-folded light curve plot...")
folded_lc = flat_lc.fold(period=best_period, epoch_time=transit_time)
binned_lc = folded_lc.bin(time_bin_size=0.003)

fig, ax = plt.subplots(figsize=(9, 5))
folded_lc.scatter(ax=ax, c="gray", alpha=0.3, s=8, label="Kepler Observations")
binned_lc.plot(ax=ax, c="crimson", lw=2.5, label="Binned Transit Profile")

ax.set_xlim(-0.06, 0.06)
ax.set_ylim(0.9992, 1.0006)
ax.set_title(f"Kepler-10b Transit Profile (Period: {best_period.value:.4f} days)", fontsize=13, fontweight='bold')
ax.set_xlabel("Phase [Days from Mid-Transit]", fontsize=11)
ax.set_ylabel("Normalized Flux", fontsize=11)
ax.grid(alpha=0.3, linestyle="--")
ax.legend(loc="lower right")
plt.tight_layout()

plt.savefig("kepler10b_transit.png", dpi=300)
print("Plot successfully saved as 'kepler10b_transit.png'.")
plt.show()
