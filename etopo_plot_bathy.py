# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 28/05/2026
# python version:          3

"""
Descrição:

Script para verificar arquivos ETOPO
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
import cartopy.feature as cfeature
# from glob import glob


# fnames = glob('/rotinas/etopo/*15s*.nc')

resolution = 60

ds = xr.open_mfdataset(
    f'/rotinas/etopo/*{resolution}s*.nc', autoclose=True)

if False:
    # Verificar Coordenadas

    fig, ax = plt.subplots()
    ax.plot(ds.lon)
    fig.savefig(f'/rotinas/etopo{resolution}_lon.png')

    fig, ax = plt.subplots()
    ax.plot(ds.lat)
    fig.savefig(f'/rotinas/etopo{resolution}_lat.png')

# Area -------------------------
lat_min, lat_max = -14.5, 15.2
lon_min, lon_max = -65.2, -29.2
# ------------------------------

if ds.lat[0] > ds.lat[-1]:
    area = ds.sel(
        lat=slice(lat_max, lat_min), lon=slice(lon_min, lon_max))

else:
    area = ds.sel(
        lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

projection = ccrs.Mercator()

fig, ax = plt.subplots(subplot_kw=dict(projection=projection))

# Limites na projeção PlateCarree (graus geográficos),
# Cartopy converte para Mercator
ax.set_extent(
    [lon_min, lon_max, lat_min, lat_max],
    crs=ccrs.PlateCarree())

if False:

    area['z'].plot.pcolormesh(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=plt.cm.terrain,
        add_colorbar=True,
        cbar_kwargs={'label': 'profundidade [m]'}
    )

cmap = 'Blues'  # apenas para nome figura

colors = plt.cm.Blues(np.linspace(.98, .2, 256))

new_cmap = new_cmap = ListedColormap(colors)

# cor_dos_rios = new_cmap.colors[-1]

vmax = 0
vmin = area.z.min().compute()

# Pegando apenas batimetria
bathy = area['z'].where(area['z'] <= vmax)

# Batimetria
mesh = bathy.plot.pcolormesh(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap=new_cmap, vmin=vmin, vmax=vmax,
    cbar_kwargs={
        # 'label': 'profundidade [m]',
        'orientation': 'vertical',
        'pad': .04,
        'shrink': .7,    # % que ocupa do eixo do mapa
        'aspect': 35},   # quanto maior, mais fina
    zorder=0)

cbar = mesh.colorbar
cbar.ax.set_ylabel(
    'Profundidade [m]', rotation=-90, labelpad=15)

# Isóbatas
c = bathy.plot.contour(
    ax=ax,
    transform=ccrs.PlateCarree(),
    levels=[-200,],
    colors=['#454545',],
    linewidths=.5,
    linestyles=['-',],
    zorder=1)

ax.clabel(
    c, fmt={-200: '200m', -100: '100m', },
    inline=True, fontsize=9, colors='#454545', zorder=1)

cres = '50m'  # regional

# Preenchimento continentes
ax.add_feature(
    cfeature.LAND.with_scale(cres), facecolor='.8', zorder=2)

# Linha de Costa
ax.coastlines(
    resolution=cres, color='.4', linewidth=.8, zorder=3)

# Corpos de Água interiores
# ax.add_feature(
#         cfeature.LAKES.with_scale(cres),
#         edgecolor='b', alpha=.2, zorder=4)

# Rios
ax.add_feature(
    cfeature.RIVERS.with_scale(cres),
    edgecolor="#5E9BF1",
    linewidth=.7,
    alpha=.7,
    zorder=4)

# Limites Estados
ax.add_feature(
    cfeature.STATES.with_scale(cres),
    edgecolor='.4', alpha=.5, linewidth=.2,
    zorder=3)

# Fronteiras Iternacionais
ax.add_feature(
    cfeature.BORDERS.with_scale(cres),
    edgecolor='.4', alpha=.9, linewidth=.5,
    zorder=3)

# Grid de latitudes e longitudes
gl = ax.gridlines(
    draw_labels=True,
    crs=ccrs.PlateCarree(),
    linewidth=.8,
    color='gray',
    alpha=.8,
    linestyle=':',
    zorder=5)

gl.top_labels = False
gl.right_labels = False

# Forçar moldura do mapa acima (estava ficando sobreposta pelo continente)
ax.spines['geo'].set_zorder(10)

ax.set_title(
    f'Mapa Batimétrico\nETOPO (Resolução {resolution}s de arco)')

fig.savefig(
    f'/rotinas/etopo_batimetria{resolution}_{cmap.lower()}.png')
