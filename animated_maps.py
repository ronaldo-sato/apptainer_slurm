# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 03/06/2025
# python version:          3


import os
import sys

import re
import xarray as xr

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# import math
import numpy as np
import pandas as pd
from pandas import date_range

import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import ffmpeg

plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'


def make_map(
        dataset,
        lonLim=['', ''],
        latLim=['', ''],
        projection=ccrs.Mercator(),
        resolution='10m',
        label_step=2,
        use_GSHHS=False,
        scale='full',
        add_LAKES=False,
        colorbar=False,
        **kwargs):

    kw_fig = dict(figsize=(9, 6), facecolor='w')

    kw_fig = {
        key: kwargs.get(key, value)
        for key, value in kw_fig.items()}

    fig, ax = plt.subplots(
        subplot_kw=dict(projection=projection), **kw_fig)

    fig.subplots_adjust(left=.07, right=.85)

    if colorbar:

        # cbax = fig.add_axes(
            # [.88, .15, .015, .7]) # left, bottom, width, height
        
        if variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

            cbax = ax.inset_axes([1.03, .2, .015, .8], transform=ax.transAxes)

        elif variable in ['ssh', 'saln', 'temp']:

            cbax = ax.inset_axes([1.03, .05, .015, .9], transform=ax.transAxes)

    offsetLim = max(
        [np.diff(ds['lon']).mean(), np.diff(ds['lat']).mean()])

    if all(True if not _lon.strip() else False for _lon in lonLim) \
            and all(True if not _lat.strip() else False for _lat in latLim):

        lonLim = [ds['lon'].min(), ds['lon'].max()]

        latLim = [ds['lat'].min(), ds['lat'].max()]

    lonLim = [lonLim[0] - 2*offsetLim, lonLim[-1] + offsetLim]

    latLim = [latLim[0] - 2*offsetLim, latLim[-1] + offsetLim]

    extent = [*lonLim, *latLim]

    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # kw_title = dict(fontsize=14, fontweight='roman')

    # kw_title = {
    #     key: kwargs.get(key, value)
    #     for key, value in kw_title.items()}

    # title = ' '.join(
    #     [item.upper() if not item.isnumeric()
    #      else rf'{item[0]}/{item[1:]}°'
    #      for item in dataset.split('_')]
    #      + [f'(Profundidade {int(depth)}m)'])

    # ax.set_title(title, **kw_title)

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
    if ds['lat'].min() < 0. and ds['lat'].max() > 0.:

        ylocs = np.unique(
            np.array([
                *np.arange(0, latLim[-1], label_step),
                *np.arange(0., latLim[0], -label_step)[::-1]
            ]))

    else:

        ylocs = range(*map(int, lonLim), label_step)

    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=draw_labels,
        xlocs=range(*map(int, lonLim), label_step),
        ylocs=ylocs,
        linestyle='--',
        linewidth=.5,
        color='k',
        alpha=0.3,
        zorder=3)

    gl.top_labels = gl.right_labels = False

    if PLOT_POINT:

        if variable == 'temp':

            color = 'k'

        else:

            color = 'r'

        ax.plot(
            lon_point,
            lat_point,
            marker='o',
            color=color,
            transform=ccrs.PlateCarree(),
            markersize=3,
            zorder=5)

        ax.text(
            1.03,  # lon_point-2,
            .93,  # lat_point-.7,
            f'\u2022 {point_name.capitalize()}',
            color=color,
            transform=ax.transAxes,  # ccrs.PlateCarree(),
            fontsize=12,
            fontweight='roman', # semibold
            horizontalalignment='left',  # center
            verticalalignment='bottom',  # center
            zorder=5)

    if colorbar:

        return fig, ax, cbax

    else:

        return fig, ax


def animate_maps(
        date,
        **kwargs):

    if variable in ['ssh', 'mld']:

        cmap = plt.cm.Spectral_r

    elif variable in ['saln']:

        # cmap = plt.cm.viridis

        from matplotlib.colors import ListedColormap

        cmap = plt.get_cmap('viridis')

        cmap = ListedColormap(cmap(np.linspace(.02, .98, 256)))

    elif variable in ['temp']:

        from matplotlib.colors import ListedColormap

        cmap = plt.get_cmap('RdYlBu_r')

        cmap = ListedColormap(cmap(np.linspace(.05, .95, 256)))

    elif variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

        # cmap = plt.cm.Blues

        from matplotlib.colors import ListedColormap

        cmap = plt.get_cmap('Blues')

        cmap = ListedColormap(cmap(np.linspace(0., .95, 256)))

    if date == start:

        if variable in ['ssh', 'mld', 'saln', 'temp']:

            label = (
                f"{ds[variable].attrs['long_name']}".title() + 
                f" [{ds[variable].attrs['units']}]")

            extend = 'both'

            if variable in ['ssh', 'mld']:

                _map = ds[variable].sel(time=date).plot.pcolormesh(
                    ax=ax,
                    transform=ccrs.PlateCarree(),
                    cmap=cmap,
                    # robust=True,
                    vmin=vmin,
                    vmax=vmax,
                    extend=extend,
                    cbar_ax=cax,
                    add_colorbar=True,
                    zorder=1)

            elif variable in ['saln', 'temp']:

                _map = ds[variable].sel(depth=depth, time=date) \
                    .plot.pcolormesh(
                        ax=ax,
                        transform=ccrs.PlateCarree(),
                        cmap=cmap,
                        # robust=True,
                        vmin=vmin,
                        vmax=vmax,
                        extend=extend,
                        cbar_ax=cax,
                        add_colorbar=True,
                        zorder=1)

        elif variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

            label = (
                'Intensidade Corrente' + 
                f" [{ds[variable[0]].attrs['units']}]")

            extend = 'max'

            _map = ds['spd'].sel(depth=depth, time=date).sel(
                lat=slice( None, None, step_pcolor),
                lon=slice(None, None, step_pcolor)
                    ).plot.pcolormesh(
                        ax=ax,
                        transform=ccrs.PlateCarree(),
                        cmap=cmap,
                        # robust=True,
                        vmin=vmin,
                        vmax=vmax,
                        extend=extend,
                        cbar_ax=cax,
                        add_colorbar=True,
                        zorder=1)

        cbar = fig.colorbar(
            _map, cax=cax, orientation='vertical', shrink=.8, extend=extend)

        # cbar.set_ticks(ticks)
        # ticklabels = cbar.ax.get_yticklabels()
        # cbar.ax.set_yticklabels(ticklabels, ha='right')

        tick_locator = mticker.MaxNLocator(nbins=6)
        cbar.locator = tick_locator
        cbar.update_ticks()

        if any(v < 0 for v in _map.get_clim()):

            pad = 10

        else:

            pad = 7

        cbar.ax.yaxis.set_tick_params(pad=pad)

        cbar.set_label(
            label, rotation=270, fontsize=13, fontweight='roman', labelpad=20)

    else:

        if variable in ['ssh', 'mld']:

            _map = ds[variable].sel(time=date).plot.pcolormesh(
                ax=ax,
                transform=ccrs.PlateCarree(),
                cmap=cmap,
                # robust=True,
                vmin=vmin,
                vmax=vmax,
                add_colorbar=False,
                zorder=1)

        elif variable in ['saln', 'temp']:

            _map = ds[variable].sel(depth=depth, time=date).plot.pcolormesh(
                ax=ax,
                transform=ccrs.PlateCarree(),
                cmap=cmap,
                # robust=True,
                vmin=vmin,
                vmax=vmax,
                add_colorbar=False,
                zorder=1)

        elif variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

            _map = ds['spd'].sel(depth=depth, time=date).sel(
                lat=slice( None, None, step_pcolor),
                lon=slice(None, None, step_pcolor)
                    ).plot.pcolormesh(
                        ax=ax,
                        transform=ccrs.PlateCarree(),
                        cmap=cmap,
                        # robust=True,
                        vmin=vmin,
                        vmax=vmax,
                        extend='max',
                        add_colorbar=False,
                        zorder=1)

    maps.append(_map)

    kw_title = dict(fontsize=14, fontweight='roman')

    kw_title = {
        key: kwargs.get(key, value)
        for key, value in kw_title.items()}

    title = ' '.join(
        [item.upper() if not item.isnumeric()
         else rf'{item[0]}/{item[1:]}°'
         for item in dataset.split('_')]
         + [f'(Profundidade {int(depth)}m)'])

    ax.set_title(title, **kw_title)

    kw_text = dict(fontsize=12, fontweight='roman')

    kw_text = {
        key: kwargs.get(key, value)
        for key, value in kw_text.items()}

    if variable in ['ssh', 'mld', 'saln', 'temp']:

        _time = ds.coords['time'] \
            .loc[date].dt.strftime(r'%d-%m-%Y %Hh').item()

        text = f'{_time}'

    elif variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

        _time = ds.coords["time"] \
            .loc[date].dt.strftime(r'%d-%m-%Y %Hh').item()

        text = f'{_time}'

    if date.month < 8:

        bbox = dict(
            boxstyle='round', facecolor='whitesmoke', pad=.3, alpha=1)

    else:

        bbox = dict(
            boxstyle='round', facecolor='darkgrey', pad=.3, alpha=1)

    ax.text(
        ds['lon'][int(ds.coords['lon'].size * .05)],
        ds['lat'][int(ds.coords['lat'].size * .05)],
        text,
        transform=ccrs.PlateCarree(),
        bbox=bbox,
        **kw_text)

    if variable in ['ssh', 'mld', 'saln', 'temp']:

        return maps

    elif variable in [['uvel', 'vvel'], ['vvel','uvel']] or PLOT_VECTORS:

        return None


def init_quiver(arrow_factor=.75):
    
    kw_quiver = dict(
        scale=30,
        width=1.5e-3,
        headlength=6,
        headwidth=3,
        headaxislength=5,
        angles='uv',
        pivot='tail')

    q = ax.quiver(
        ds['lon'].sel(lon=slice(None, None, step_quiver)),
        ds['lat'].sel(lat=slice(None, None, step_quiver)),
        np.nan * ds['uvel'].sel(depth=depth, time=slice(start, end)) \
            .isel(time=0).sel(
                lon=slice(None, None, step_quiver),
                lat=slice(None, None, step_quiver)) \
            .values,
        np.nan * ds['vvel'].sel(depth=depth, time=slice(start, end)) \
            .isel(time=0).sel(
                lon=slice(None, None, step_quiver),
                lat=slice(None, None, step_quiver)) \
            .values,
        transform=ccrs.PlateCarree(),
        **kw_quiver,
        color=color,
        alpha=.9,
        zorder=4)

    qkey = ax.quiverkey(
        q, .83, .77,
        2.*arrow_factor, r'$2\;\frac{m}{s}$',
        labelpos='S', coordinates='figure',
        color='k', labelsep=.07,
        transform=ccrs.PlateCarree())

    ax.text(
        1.03,
        .3,
        f'Velocidade Máxima:\n\n{vmax.isel(time=0).item():.2f}',
        transform=ax.transAxes,
        fontsize=12,
        fontweight='roman',
        horizontalalignment='left',
        verticalalignment='bottom',
        zorder=5)

    return q, qkey


def animate_quiver(date, q, arrow_factor=.75):

    animate_maps(date)

    q.set_UVC(
        ds['uvel'].sel(time=date, depth=depth).sel(
            lon=slice(None, None, step_quiver),
            lat=slice(None, None, step_quiver))*arrow_factor,
        ds['vvel'].sel(time=date, depth=depth).sel(
            lon=slice(None, None, step_quiver),
            lat=slice(None, None, step_quiver))*arrow_factor)

    ax.text(
        1.03,
        .3,
        f'Velocidade Máxima:\n\n{vmax.sel(time=date).item():.2f}',
        transform=ax.transAxes,
        fontsize=12,
        fontweight='roman',
        horizontalalignment='left',
        verticalalignment='bottom',
        zorder=5)

    return q,


def date_format(date):
    '''
    Determina o formato da data.
    '''

    if re.match('^\d{4}$', date):

        fmt = '%Y'

    elif re.match('^\d{4}[-/]\d{2}$', date):

        sep = re.search('^\d{4}([-/])\d{2}$', date).group(1)

        fmt = f'%Y{sep}%m'

    elif re.match('^\d{4}([-/]\d{2})+$', date):

        sep = re.search('^\d{4}(([-/])\d{2}){2}', date).group(2)

        fmt = f'%Y{sep}%m{sep}%d'

    elif re.match('^\d{2}[-/]\d{4}$', date):

        sep = re.search('^\d{2}([-/])\d{4}$', date).group(1)

        fmt = f'%m{sep}%Y'

    elif re.match('^\d{2}[-/]\d{2}[-/]\d{4}$', date):

        sep = re.search('^(\d{2}([-/])){2}\d{4}$', date).group(2)

        fmt = f'%d{sep}%m{sep}%Y'

    elif re.match('^$', date):
        
        fmt = ''

    return fmt


def months_list(date, fmt):
    '''
    Gerar lista de meses a partir do padrão do formato de data.
    '''
    months = []

    if not isinstance(date, list):

        date = [date]

    if not isinstance(fmt, list):

        fmt = [fmt]

    for date_, fmt_ in zip(date, fmt):

        # Para um ano todo.
        if re.match('^%Y$', fmt_):

            months += [
                (datetime.strptime(date_, fmt_) + \
                    relativedelta(months=i)).strftime(fmt_)
                for i in range(0, 13)]

        # Para um mês.
        elif re.match('^%Y[-/]%m([-/]%d)*$', fmt_):

            # Para n meses a partir do mês (contando o início)
            if n_months:

                months += [
                    (datetime.strptime(date_, fmt_) + \
                        relativedelta(months=i)).strftime(fmt_)
                    for i in range(int(n_months))]

            # embora condição acima, aparentemente, suficiente para todos casos
            else:

                months += [datetime.strptime(date_, fmt_)]

        # Para Período Completo (Vazios):
        elif not date_.strip() and not fmt_.strip():

            months += ['all']

    return months


def fmt_list(fmt, n_months):
    '''
    Gerar lista de formatos com tamanho correspondente ao de datas.
    '''

    _fmt = [[item]*int(n_months) for item in fmt]

    return [item for sublist in _fmt for item in sublist]


def uv2spddir(u, v):
    """
    Cálculo da velocidade e direção, respectivamente 'spd' e 'drc', 
    a partir das componentes de velocidade (u e v).
    """

    spd = np.sqrt(u**2 + v**2)

    drc = np.rad2deg(np.arctan2(u, v)) % 360

    return spd, drc


if __name__ == '__main__':

    import json
    # from pathlib import Path

    # Mapeamento Contêiner

    path_data = '/base'
    path_anim = '/anim'
    path_local = '/rotinas'

    with open(
        '/'.join([path_local, 'input_animations.json'])) as f:

        daux = json.load(f)

    dataset = daux['dataset']             # nome base de dados
    lonLim = sorted(daux['lonLim'])       # limite meridional
    latLim = sorted(daux['latLim'])       # limite setentrional
    date = daux['date']                   # ano(-mês) para criar mapas
    n_months = daux['n_months']           # número de meses
    variable = daux['variable']           # variável plotada
    depth = daux['depth']                 # profundidade dos dados
    anim_path = daux['anim_path']         # pasta para salvar animações

    # Determinar limites geográficos (se não forem vazios).

    # se for string
    if any(isinstance(_lon, str) for _lon in lonLim) or \
            any(isinstance(_lat, str) for _lat in latLim):

        # se não for vazia
        if all(_lon.strip() for _lon in lonLim) and \
                all(_lat.strip() for _lat in latLim):

            lonLim = [float(_lon) for _lon in lonLim]
            latLim = [float(_lat) for _lat in latLim]

    # Ordenar coordenadas (crescente).
    if lonLim[0] > lonLim[-1]:

        lonLim = lonLim[::-1]

    if latLim[0] > latLim[-1]:

        latLim = latLim[::-1]

    if isinstance(n_months, int):

        # f = lambda n: int(n) if str(n_months).strip() else 1

        n_months = str(n_months)

    if anim_path:

        if isinstance(anim_path, str):

            path_anim = '/'.join([path_anim, anim_path])

        elif isinstance(anim_path, list):

            path_anim = '/'.join([path_anim, *anim_path])

    PLOT_VECTORS = json.loads(
        daux.get('PLOT_VECTORS').lower()) # se plota vetores ou não

    PLOT_POINT = json.loads(
        daux.get('PLOT_POINT').lower())  # se plota ponto M

    if PLOT_POINT:

        sys.path.insert(0, path_local)

        from __aux__ import *

    # Leitura Dados

    ds = xr.open_mfdataset(f'{path_data}/*.nc', autoclose=True)

    # Renomeando / padronizando long_name

    for _variable in list(ds.variables):

        # Definindo e ajustando long_names.
        if _variable == 'ssh':

            ds[_variable].attrs['long_name'] = 'sea surface height'

        elif _variable == 'mld':

            ds[_variable].attrs['long_name'] = \
                ' '.join(ds[_variable].attrs['long_name'].split('_'))

        # Acertando long_name em maiúsculo.
        ds[_variable].attrs['long_name'] = \
            f"{ds[_variable].attrs['long_name']}".title()

    # Setar Variáveis

    # ['ssh', 'saln', 'temp', 'mld', ['uvel', 'vvel']]

    if PLOT_VECTORS:

        _variable = ['uvel', 'vvel']

    if variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

        PLOT_VECTORS = False

    if variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

        # vmin, vmax = 0., .5
        vmin = 0

        # vmax = ds['spd'].max(dim='time').compute()

    # Definir Formato de Data
    if isinstance(date, str):

        fmt = [date_format(date)]

    elif isinstance(date, list):

        # Se um item da lista for vazio
        if any(True if not _date.strip() else False for _date in date):

            date = [_date for _date in date if _date]

        fmt = [date_format(_date) for _date in date]

        # Verificar diferença entre as datas
        # if len(date) == 2:

        #     dt1 = datetime.strptime(date[0], fmt[0])
        #     dt2 = datetime.strptime(date[1], fmt[1])
            
        #     if dt2.month - dt1.month > 2:
                
        #         date = 

    months = months_list(date, fmt)

    if int(n_months.strip() or 1) > 1:

        fmt = fmt_list(fmt, n_months)

    # Se forem vazios, para fazer para o período todo:
    # OBS: Período todo aparentemente a máquina não faz
    # Fazer por meses separados e juntar com ffmpeg depois
    if not fmt and not months:

        months, fmt = [''], [''] # precisam ser listas de string vazia

    for month, _fmt in zip(months, fmt):

        # Primeiro e último dias do mês (animações mensais)

        if _fmt and month:

            start = datetime.strptime(month, _fmt)
            end = start + relativedelta(months=1) - timedelta(days=1)

        else:

            start = pd.Timestamp(ds['time'][0].values).to_pydatetime()
            end = pd.Timestamp(ds['time'][-1].values).to_pydatetime()

        # Mapas

        maps = []

        fig, ax, cax = make_map(
            dataset, lonLim, latLim, label_step=5, colorbar=True)

        if PLOT_VECTORS or variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

            step_quiver = 36 // 2 # 111.11 / (36 // 2) = ~6 km

            if variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

                step_pcolor = 2

                color = 'k'

                if 'spd' not in list(ds.variables):

                    ds['spd'], ds['dir'] = uv2spddir(ds['uvel'], ds['vvel'])

                    vmax = ds['spd'].sel(depth=depth) \
                                    .max(dim=['lat', 'lon']).compute()

            elif variable in ['ssh', 'mld', 'saln', 'temp']:

                step_pcolor = 5

                if variable == 'saln':

                    color = 'w'

                else:

                    color = 'k'

            arrow_factor = .75

            q, qkey = init_quiver()

            anim = FuncAnimation(
                fig, animate_quiver, fargs=(q,),
                frames=date_range(start, end),#, freq='2D'),
                init_func=None, interval=300, blit=True)

        else:

            anim = FuncAnimation(
                fig, animate_maps,
                frames=date_range(start, end),#, freq='2D'),
                init_func=None, interval=300, blit=True)

        if variable in [['uvel', 'vvel'], ['vvel', 'uvel']]:

            _variable = 'uvelvvel'

        else:

            _variable = variable

        if not os.path.exists(f'{path_anim}/{_variable}/{depth}m'):

            if not os.path.exists(f'{path_anim}/{_variable}'):

                os.mkdir(f'{path_anim}/{_variable}')

            else:

                os.mkdir(f'{path_anim}/{_variable}/{depth}m')

        if PLOT_POINT and PLOT_VECTORS:

            filename = (
                f'{path_anim}/{_variable}/{depth}m/'
                f'{dataset}_{_variable}_{depth}m'
                f"_{start.strftime(r'%Y%m%d')}-{end.strftime(r'%Y%m%d')}"
                f"_{point_name.lower()}_vel.mp4")

        elif PLOT_POINT and not PLOT_VECTORS:

            filename = (
                f'{path_anim}/{_variable}/{depth}m/'
                f'{dataset}_{_variable}_{depth}m'
                f"_{start.strftime(r'%Y%m%d')}-{end.strftime(r'%Y%m%d')}"
                f"_{point_name.lower()}.mp4")

        else:

            filename = (
                f'{path_anim}/{_variable}/{depth}m/'
                f'{dataset}_{_variable}_{depth}m'
                f"_{start.strftime(r'%Y%m%d')}-{end.strftime(r'%Y%m%d')}.mp4")

        anim.save(filename=filename, writer='ffmpeg')

        print(f'Animação para {variable} {month} foi salva.')

    print('Fim do programa.')
