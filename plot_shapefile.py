# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 28/11/2025
# python version:          3

import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import json


def make_map(
        dataset='',
        lonLim=['', ''],
        latLim=['', ''],
        projection=ccrs.Mercator(),
        resolution='10m',
        label_step=2,
        use_GSHHS=False,
        scale='full',
        add_LAKES=False,
        title='',
        point=[],
        **kwargs):

    kw_fig = dict(figsize=(9, 6), facecolor='w')

    kw_fig = {
        key: kwargs.get(key, value)
        for key, value in kw_fig.items()}

    fig, ax = plt.subplots(
        subplot_kw=dict(projection=projection), **kw_fig)

    fig.subplots_adjust(left=.07, right=.85)

    extent = [*lonLim.squeeze(), *latLim.squeeze()]

    ax.set_extent(extent, crs=ccrs.PlateCarree())

    if title:

        kw_title = dict(fontsize=20, fontweight='roman')

        kw_title = {
            key: kwargs.get(key, value)
            for key, value in kw_title.items()}

        ax.set_title(title, **kw_title)

    ax.add_feature(
        cfeature.LAND.with_scale(resolution),
        facecolor='.85', zorder=1)

    if not use_GSHHS:

        ax.coastlines(
            resolution=resolution,
            linewidth=.5, edgecolor='.4', zorder=3)

    else:

        coastline = cfeature.GSHHSFeature(
            scale=scale, edgecolor='.4', zorder=3)

        ax.add_feature(coastline, facecolor='.85')

    if add_LAKES:

        ax.add_feature(
            cfeature.LAKES.with_scale(resolution),
            edgecolor='b', alpha=.2, zorder=3)

        ax.stock_img()  # add an underlay image

    ax.add_feature(
        cfeature.STATES.with_scale(resolution),
        edgecolor='.4', alpha=.5, linewidth=.2,
        zorder=2)

    ax.add_feature(
        cfeature.BORDERS.with_scale(resolution),
        edgecolor='.4', alpha=.9, linewidth=.5,
        zorder=3)

    draw_labels = (projection == ccrs.PlateCarree() or
                   projection == ccrs.Mercator())

    # if ds['lat'].min() < 0. and ds['lat'].max() > 0.:
    if latLim.min() < 0. and latLim.max() > 0.:

        ylocs = np.unique(
            np.array([
                *np.arange(0, latLim.squeeze()[-1], label_step),
                *np.arange(0., latLim.squeeze()[0], -label_step)[::-1]
            ]))

    else:

        ylocs = range(*map(int, latLim.squeeze()), label_step)

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=draw_labels,
        xlocs=range(*map(int, lonLim.squeeze()), label_step),
        ylocs=ylocs,
        linestyle='--',
        linewidth=.5,
        color='k',
        alpha=0.3,
        zorder=3)

    gl.top_labels = gl.right_labels = False

    gl.xlabel_style = {'size': 12}
    gl.ylabel_style = {'size': 12}

    if point:

        ax.plot(
            point[0],
            point[-1],
            marker='o',
            color='r',
            transform=ccrs.PlateCarree(),
            markersize=3,
            zorder=5)

    return fig, ax


def plot_shapefile():

    from cartopy.io.shapereader import Reader
    from cartopy.feature import ShapelyFeature

    fig, ax = make_map(
        'teste', lonLim_map, latLim_map, label_step=2)

    shape_manobra = ShapelyFeature(
        Reader(
            path_base + f'/{path_shapefile}/manobra/area_manobra.shp')
        .geometries(),
        ccrs.PlateCarree(),
        edgecolor='b',
        facecolor='none')

    shape_aquisicao = ShapelyFeature(
        Reader(
            path_base + f'/{path_shapefile}/aquisicao/area_aquisicao.shp')
        .geometries(),
        ccrs.PlateCarree(),
        edgecolor='r',
        facecolor='none')

    ax.add_feature(shape_manobra)
    ax.add_feature(shape_aquisicao)

    fig.savefig(f'{path_local}/_teste_mapa_shapefile.png', format='png')

    return None


if __name__ == '__main__':

    # Mapeamento Contêiner
    path_local = '/rotinas'
    path_base = '/base'

    with open(
            '/'.join([path_local, 'input_plot_shapefile.json'])) as f:

        daux = json.load(f)

    dataset = daux['dataset']                # nome da base de dados
    start = daux['start']                    # data inicial
    end = daux['end']                        # data final
    year = daux['year']                      # ano específico
    depth = daux['depth']                    # profundidade
    lon = daux['lon']                        # longitude para um ponto
    lat = daux['lat']                        # latitude para um ponto
    lonLim_map = daux['lonLim']              # limites longitude para o mapa
    latLim_map = daux['latLim']              # limites latitude para o mapa
    variables = daux['variables']            # lista de variáveis
    path_shapefile = daux['path_shapefile']  # pasta onde salvar os dados

    BATHY = json.loads(daux.get('batimetria').lower())

    manobra = gpd.read_file(
        path_base + f'/{path_shapefile}/manobra/area_manobra.shp')

    aquisicao = gpd.read_file(
        path_base + f'/{path_shapefile}/aquisicao/area_aquisicao.shp')

    # bounds = manobra.bounds

    lonLim_manobra = manobra.bounds[['minx', 'maxx']].values  # .tolist()
    latLim_manobra = manobra.bounds[['miny', 'maxy']].values  # .tolist()

    lonLim_aquisicao = aquisicao.bounds[['minx', 'maxx']].values
    latLim_aquisicao = aquisicao.bounds[['miny', 'maxy']].values

    lonLim_map, latLim_map = np.array(lonLim_map), np.array(latLim_map)

    fig, ax = make_map(
        'teste', lonLim_map, latLim_map, label_step=2)

    title = 'Área Sísmica'

    if BATHY:
        import xarray as xr
        from matplotlib.colors import ListedColormap

        cmap = 'Blues'  # apenas para nome figura
        res = 60        # resolução ETOPO

        colors = plt.cm.Blues(np.linspace(.98, .2, 256))

        new_cmap = ListedColormap(colors)

        ds = xr.open_mfdataset(
            f'/rotinas/etopo/*{res}s*.nc', autoclose=True)

        area = ds.sel(
            lat=slice(*sorted(latLim_map)),
            lon=slice(*sorted(lonLim_map)))

        vmax = 0
        vmin = area.z.min().compute()

        # Pegando apenas batimetria
        bathy = area['z'].where(area['z'] <= vmax)

        # Setar valores acima de zero (preencher buracos em branco)
        # com a cor do zero.
        # Pegar cor do zero
        zero_color = new_cmap(1.0)

        # Define cor do zero para valores acima do vmax
        new_cmap.set_over(zero_color)
        # Define cor do zero para valores mascarados NaN
        new_cmap.set_bad(zero_color)

        # Batimetria
        mesh = bathy.plot.pcolormesh(
            ax=ax,
            transform=ccrs.PlateCarree(),
            cmap=new_cmap,
            vmin=vmin,
            vmax=vmax,  # valores acima na cor definida por set_over
            cbar_kwargs={
                # 'label': 'profundidade [m]',
                'orientation': 'vertical',
                'pad': .04,
                'shrink': .7,    # % que ocupa do eixo do mapa
                'aspect': 35,    # quanto maior, mais fina
                # matplotlib mais recente poderia:
                # 'label_kwargs': {'fontsize': 12, 'labelpad': 15},
                # 'tick_params': {'labelsize': 10}
            },
            zorder=0)

        # cbar.ax.yaxis.label.set_rotation(-90)

        cbar = mesh.colorbar
        cbar.ax.set_ylabel(
            'Profundidade [m]',
            fontsize=14,
            rotation=-90,
            labelpad=20)

        cbar.ax.tick_params(labelsize=11)

        # Isóbatas
        # levels = [-200]
        levels = [-200, -1000, -2000, -3000, -4000]

        c = bathy.plot.contour(
            ax=ax,
            transform=ccrs.PlateCarree(),
            levels=levels,
            colors=['#333333',],
            linewidths=.4,
            linestyles=['-',],
            zorder=1)

        fmt = {-200: '200m',
               -100: '100m',
               -500: '500m',
               -1000: '1000m',
               -2000: '2000m',
               -3000: '3000m',
               -4000: '4000m'}

        ax.clabel(
            c, fmt=fmt,
            inline=True, fontsize=9, colors='#333333', zorder=1)

        title += f'\nMapa Batimétrico (ETOPO {res}s)'

        fig.subplots_adjust(bottom=.07, top=.87)

    if not BATHY:
        fig.subplots_adjust(bottom=.07, top=.91)

    ax.set_title(title, fontsize=16, pad=17)

    # Plotando Shapefiles
    _ = manobra.plot(
        facecolor='none',
        edgecolor='red',
        lw=1,
        ax=ax,
        transform=ccrs.PlateCarree(),
        legend=True,
        legend_kwds={'label': 'Manobra',
                     'orientation': 'vertical'},
        zorder=3)

    _ = aquisicao.plot(
        facecolor='none',
        edgecolor='black',
        lw=1,
        ax=ax,
        transform=ccrs.PlateCarree(),
        legend=True,
        legend_kwds={'label': 'Aquisição',
                     'orientation': 'vertical'},
        zorder=3)

    # Plotar textos associados
    offset = .1

    ax.text(
        lonLim_manobra[0][0],
        latLim_manobra[0][1],
        'Manobra',
        ha='left',
        va='bottom',
        transform=ccrs.PlateCarree(),
        fontsize=11,
        color='r',
        zorder=3)

    ax.text(
        lonLim_aquisicao[0][1],
        latLim_aquisicao[0][0] - offset,
        'Aquisição',
        ha='right',
        va='top',
        transform=ccrs.PlateCarree(),
        fontsize=11,
        color='k',
        zorder=3)

    fig.savefig(
        f'{path_local}/batimetria_area_aquisicao_sismica_teste.png',
        format='png')
