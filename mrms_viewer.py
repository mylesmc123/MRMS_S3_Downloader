import os
import gzip
import pygrib
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from datetime import datetime
from matplotlib.animation import FuncAnimation
import shutil
import tempfile

# === CONFIG ===
data_dir = "./mrms_qpe/uncompressed"  # Directory with .grib2.gz files
center_lat = 34.6036     # Lawton, OK latitude
center_lon = -98.3959    # Lawton, OK longitude
extent_deg = 2.0         # +/- degrees around Lawton to show

output_gif = "lawton_qpe_animation.gif"

# === HELPER FUNCTIONS ===
def read_grib_file(filepath):
    if filepath.endswith(".gz"):
        with gzip.open(filepath, 'rb') as f_in:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfileobj(f_in, tmp)
                tmp_path = tmp.name
        grbs = pygrib.open(tmp_path)
    else:
        grbs = pygrib.open(filepath)
    return grbs

def plot_frame(msg, ax, vmin, vmax):
    lats, lons = msg.latlons()
    data = msg.values

    ax.clear()
    ax.set_extent([center_lon - extent_deg, center_lon + extent_deg,
                   center_lat - extent_deg, center_lat + extent_deg], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.STATES.with_scale('10m'))
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    time = datetime(msg.dataDate // 10000, (msg.dataDate // 100) % 100, msg.dataDate % 100,
                    msg.dataTime // 100, msg.dataTime % 100)

    time_str = time.strftime('%Y-%m-%d %H:%M UTC')
    ax.set_title(f"MRMS Precip 1hr - {time_str}", fontsize=12)

    pcm = ax.pcolormesh(lons, lats, data, cmap='turbo', transform=ccrs.PlateCarree(),
                        shading='auto', vmin=vmin, vmax=vmax)
    return pcm

# === MAIN ===
files = sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".grib2") or f.endswith(".grib2.gz")])

# Preload GRIB messages for speed
grib_messages = []
for f in files:
    grbs = read_grib_file(f)
    grib_messages.append(grbs.message(1))  # Store only the message, not whole grbs object
    grbs.close()

# Get min/max values
vmin = min(msg.values.min() for msg in grib_messages)
vmax = max(msg.values.max() for msg in grib_messages)

# Setup figure
fig = plt.figure(figsize=(8, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot first frame to create colorbar properly
pcm = plot_frame(grib_messages[0], ax, vmin, vmax)
cbar = fig.colorbar(pcm, ax=ax, orientation='vertical')
cbar.set_label('Precipitation (mm/hr)')

def update(i):
    pcm = plot_frame(grib_messages[i], ax, vmin, vmax)
    return [pcm]

anim = FuncAnimation(fig, update, frames=len(grib_messages), blit=True)

# Save animation
anim.save(output_gif, writer="pillow", fps=2)

print(f"Saved animation to {output_gif}")
