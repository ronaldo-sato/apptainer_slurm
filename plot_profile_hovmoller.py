# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 30/09/2025
# python version:          3

'''Programa para plotar perfil de corrente interanual médio e
diagrama Hovmöller.
'''

import sys
import re
import xarray as xr
import numpy as np
import pandas as pd
from scipy.stats import circmean
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.cm import ScalarMappable
# import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, Normalize
# from matplotlib.colors import LinearSegmentedColormap
import json


def uv2spddir(u, v):
    """
    Cálculo da velocidade e direção, respectivamente 'spd' e 'drc', 
    a partir das componentes de velocidade (u e v).
    
    Parâmetros
    ----------
    u: array_like
        Componente zonal de velocidade
        
    v: array_like
        Componente meriodional de velocidade
        
    Retorno
    -------
    spd: array_like
        Intensidade
        
    drc: array_like
        Direção
        
    Exemplo (arrumar isto aqui)
    -------
    >>> spd, drc = uv2spddir(u, v)
    >>> spd
    >>> dir
    """

    spd = np.sqrt(u**2 + v**2)

    drc = np.rad2deg(np.arctan2(u, v)) % 360

    return spd, drc


def hovmoller_test():

    condition = (df['dir'] < 225) & (df['dir'] > 45)

    df.loc[condition, 'spd'] = (-1) * df.loc[condition, 'spd']

    # xtime = df['spd'].unstack(level='depth').index.to_numpy(dtype=float)
    # ydepth = df['spd'].unstack(level='time').index.to_numpy()

    # xtime = xtime - xtime[0]

    # xx, yy = np.meshgrid(xtime, ydepth)

    fig, ax = plt.subplots(figsize=(16, 12))

    # vmin = np.round(-(df['spd'].max()-(1*df['spd'].std())), decimals=1)
    vmin = df['spd'].min()
    vmax = np.round(df['spd'].max()-(1*df['spd'].std()), decimals=1)

    levels = np.arange(0., df['spd'].max(), .5)
    ticks = (-levels[:0:-1]).tolist() +  levels.tolist()

    cmap = plt.get_cmap('jet', 256)
    cmap = ListedColormap(cmap(np.linspace(.15, .95, 256)))
    
    norm = Normalize(vmin=vmin, vmax=vmax, clip=False)

    contourf = ax.contourf( #pcolor( #imshow(
        df['spd'].unstack(level='time').values,
        vmin=vmin,
        vmax=vmax,
        levels=100,
        cmap=cmap,
        norm=norm,
        extend='both')

    if False:

        csplus = ax.contour(
            df['spd'].unstack(level='time').values,
            levels=levels, colors='k', linewidths=.2, zorder=3)

        ax.clabel(
            csplus, levels,
            fmt='', inline=True, inline_spacing=15, fontsize=10)

        csminus = ax.contour(
            df['spd'].unstack(level='time').values,
            levels=-levels[::-1], colors='w', linewidths=.2, zorder=3)

        ax.clabel(
            csminus, -levels[::-1],
            fmt='', inline=True, inline_spacing=15, fontsize=10)

    ax.invert_yaxis()

    # cbar = fig.colorbar(
    #     contourf, fraction=.2, shrink=.75, extend='both')
        # ticks=(-levels[:0:-1]).tolist() +  levels.tolist())

    cbar = fig.colorbar(
        ScalarMappable(norm=contourf.norm, cmap=contourf.cmap),
        ax=ax, ticks=ticks, fraction=.015, shrink=.75, extend='both')

    fig.savefig(f'{path2save}/teste_hovmoller.png', format='png')

    return None


def plot_hovmoller(variable, clabel=False):

    x = df[variable].unstack(level='depth') \
        .index.get_level_values('time').astype(int)

    y = df[variable].unstack(level='time') \
        .index.get_level_values('depth')

    xx, yy = np.meshgrid(x, y)

    # df['timestamp'] = df.index.get_level_values('time').astype(int)
    
    # _df = df.reset_index().set_index(['timestamp', 'depth'])

    fig, ax = plt.subplots(figsize=(18, 12))

    if variable == 'spd':

        # vmin = np.round(-(df['spd'].max()-(1*df['spd'].std())), decimals=1)
        vmin = df['spd'].min()
        vmax = np.round(df['spd'].max()-(1*df['spd'].std()), decimals=1)

        levels = np.arange(0., df['spd'].max(), .5)
        ticks = (-levels[:0:-1]).tolist() +  levels.tolist()

        cmap = plt.get_cmap('jet', 256)
        cmap = ListedColormap(cmap(np.linspace(.15, .95, 256)))
        
        norm = Normalize(vmin=vmin, vmax=vmax, clip=False)

        contourf = ax.contourf( #pcolor( #imshow(
            # x, y,
            xx, yy,
            df[variable].unstack(level='time').values,
            vmin=vmin,
            vmax=vmax,
            levels=100,
            cmap=cmap,
            norm=norm,
            extend='both')
        
        cbar_title = 'Intensidade de Corrente [m/s]'

    elif variable == 'dir':

        vmin, vmax = 0., 360.
        levels = np.arange(0., vmax+1, 45.)
        ticks = levels.tolist()

        if False:

            cmap = plt.get_cmap('RdYlBu_r', 128)  # Spectral_r

            _colors = np.vstack((cmap(np.linspace(.0, .5, 128)),
                                 cmap(np.linspace(.0, .5, 128))[::-1]))

            _colors = np.roll(_colors, int(cmap.N*(-.25)), axis=0) #.75

            cmap = ListedColormap(_colors, name='RdYlBu_cutted')

        if True:

            cmap = plt.get_cmap('RdBu_r', 128) 

            _colors = np.vstack((cmap(np.linspace(.1, .5, 128)),
                                 cmap(np.linspace(.1, .5, 128))[::-1]))

            _colors = np.roll(_colors, int(cmap.N*(-.25)), axis=0)

            cmap = ListedColormap(_colors, name='RdBu_cutted')

            # cmap = plt.get_cmap('bwr', 128)

            # _colors = np.vstack((cmap(np.linspace(.1, .5, 128)),
            #                      cmap(np.linspace(.1, .5, 128))[::-1]))

            # _colors = np.roll(_colors, int(cmap.N*(-.25)), axis=0)

            # cmap = ListedColormap(_colors, name='bwr_cutted')

            # cmap = plt.get_cmap('jet', 256)
            # _colors = cmap(np.linspace(.15, .95, 256))
            # _colors = np.roll(_colors, int(cmap.N*(-.25)), axis=0)
            # cmap = ListedColormap(_colors, name='jet_rolled')

        norm = Normalize(vmin=vmin, vmax=vmax, clip=False)

        contourf = ax.contourf( #pcolor( #imshow(
            # x, y,
            xx, yy,
            # _df[variable].unstack(level='timestamp').values,
            # df[variable].index.get_level_values('time'),
            # df[variable].index.get_level_values('depth'),
            df[variable].unstack(level='time').values,  
            vmin=vmin,
            vmax=vmax,
            levels=100,
            cmap=cmap,
            norm=norm,
            extend='both')
        
        cbar_title = 'Direção de Corrente [°]'

    if clabel:

        cs_plus = ax.contour(
            df[variable].unstack(level='time').values,
            levels=levels, colors='k', linewidths=.2, zorder=3)

        ax.clabel(
            cs_plus, levels,
            fmt='', inline=True, inline_spacing=15, fontsize=10)

        cs_minus = ax.contour(
            df[variable].unstack(level='time').values,
            levels=-levels[::-1], colors='w', linewidths=.2, zorder=3)

        ax.clabel(
            cs_minus, -levels[::-1],
            fmt='', inline=True, inline_spacing=15, fontsize=10)

    ax.invert_yaxis()
    # ax.set_ylim(ax.get_ylim()[::-1])
    # ax.yaxis.set_inverted(True)

    ax.set_ylabel('Profundidade [m]', fontsize=22)

    ax.tick_params(axis='y', which='major', labelsize=16)

    try:

        ax.set_title(
            f'{dataset}\nPonto de grade próximo à {point_name.capitalize()}\n'
            'Diagrama Hovmöller',
            fontsize=22, pad=18)

    except NameError:

        ax.set_title(
            f'{dataset}\nPonto de grade próximo à'
            f' lat={round(ds["lat"].item(), ndigits=4)},'
            f' lon={round(ds["lon"].item(), ndigits=4)}\n'
            'Diagrama Hovmöller',
            fontsize=22, pad=18)

    cbar = fig.colorbar(
        ScalarMappable(norm=contourf.norm, cmap=contourf.cmap),
        ax=ax, ticks=ticks, fraction=.015, shrink=.75, extend='both', pad=.02)

    cbar.ax.tick_params(labelsize=18, pad=10) 

    cbar.set_label(cbar_title, rotation=270, fontsize=22, labelpad=30)

    month_labels = df[variable].index.get_level_values('time') \
        .unique().strftime('%m/%Y').unique().to_list()

    major_labels = [
        label
        for label in month_labels
        if pd.to_datetime(label, format='%m/%Y').month == 1]

    major_ticks = pd.to_numeric(
        pd.to_datetime(major_labels, format='%m/%Y')).tolist()

    _minor_labels = [
        label
        for label in month_labels
        if pd.to_datetime(label, format='%m/%Y').month in [3, 6, 9, 12]]

    minor_ticks = pd.to_numeric(
        pd.to_datetime(_minor_labels, format='%m/%Y')).tolist()

    minor_labels = [
        dt.strftime('%m')
        for dt in pd.to_datetime(month_labels, format='%m/%Y')
        if dt.month in [3, 6, 9, 12]]

    # _middle_labels = [
    #     label
    #     for label in month_labels
    #     if pd.to_datetime(label, format='%m/%Y').month in [3, 6, 9, 12]]

    # major_ticks += pd.to_numeric(
    #     pd.to_datetime(_middle_labels, format='%m/%Y')).tolist()

    # major_labels += [
    #     pd.to_datetime(label, format='%m/%Y').strftime('%m')
    #     for label in _middle_labels]

    # _ = ax.set_xticks(
    #     major_ticks+minor_ticks, major_labels+minor_labels,
    #     rotation=60, fontsize=10, ha='right')

    ax.set_xticks(
        major_ticks, major_labels, minor=False,
        rotation=90, fontsize=16, ha='center')

    ax.set_xticks(
        minor_ticks, minor_labels, minor=True,
        rotation=90, fontsize=14, ha='center')

    # for ticklabel in ax.xaxis.get_ticklabels():
        
    #     if re.match('\d+/\d+', ticklabel.get_text()):

    #         month = pd.to_datetime(ticklabel.get_text(), format='%m/%Y').month

    #         if (month % d == 0 for d in [3, 9, 11]):

    #             ticklabel.set_fontsize(15)

    # Controlar dessa forma está dando OverflowError
    # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    # ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))

    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))

    _ = ax.tick_params(
        axis='x', which='major', direction='out', bottom=True, top=True,
        labelbottom=True, labeltop=False, width=2, length=8, pad=20)

    _ = ax.tick_params(
        axis='x', which='minor', direction='out', bottom=True, top=True,
        labelbottom=True, labeltop=False, width=1, length=5)

    # ax.grid(which='major', color='grey', linestyle='--', linewidth=0.8)

    fig.subplots_adjust(left=.08, right=.92, top=.89, bottom=.13)

    fig.savefig(
        f'{path2save}/hovmoller_{variable}_'
        f'{df.index.get_level_values("time")[0].strftime(r"%b%Y")}'
        f'-{df.index.get_level_values("time")[-1].strftime(r"%b%Y")}.png',
        format='png')

    return fig, ax


def hovmoller_subplots(variable, depths=[], clabel=False):

    fig, ax = plt.subplots(
        figsize=(18, 12), nrows=len(depths), sharex=True)

    _depth = np.array(depths).flatten()
    _depth = _depth[0], _depth[-1]

    contourf = []

    for i, depth in enumerate(depths):

        x = df.loc[(slice(None), slice(*depth)), variable] \
            .unstack(level='depth') \
            .index.get_level_values('time').astype(int)

        y = df.loc[(slice(None), slice(*depth)), variable] \
            .unstack(level='time') \
            .index.get_level_values('depth')

        xx, yy = np.meshgrid(x, y)

        if variable == 'spd':

            vmin = np.round(
                df.loc[(slice(None), slice(*_depth)), variable].min(),
                decimals=1)

            vmax = np.round(
                df.loc[(slice(None), slice(*_depth)), variable].max()
                    -(1*df.loc[(slice(None), slice(*_depth)), variable].std()),
                decimals=1)

            levels = np.arange(0., df[variable].max(), .5)
            ticks = (-levels[:0:-1]).tolist() +  levels.tolist()

            cmap = plt.get_cmap('jet', 256)
            cmap = ListedColormap(cmap(np.linspace(.15, .95, 256)))
            
            norm = Normalize(vmin=vmin, vmax=vmax, clip=False)

            try:

                contourf += [
                    ax[i].contourf(
                        xx, yy,
                        df.loc[(slice(None), slice(*depth)), variable] \
                            .unstack(level='time').values,
                        vmin=vmin,
                        vmax=vmax,
                        levels=100,
                        cmap=cmap,
                        norm=norm,
                        extend='both')]
            
            except TypeError:
            
                contourf += [
                    ax.contourf(
                        xx, yy,
                        df.loc[(slice(None), slice(*depth)), variable] \
                            .unstack(level='time').values,
                        vmin=vmin,
                        vmax=vmax,
                        levels=100,
                        cmap=cmap,
                        norm=norm,
                        extend='both')]
            
            cbar_title = 'Intensidade de Corrente [m/s]'

        elif variable == 'dir':

            vmin, vmax = 0., 360.
            levels = np.arange(0., vmax+1, 45.)
            ticks = levels.tolist()

            cmap = plt.get_cmap('RdBu_r', 128) 

            _colors = np.vstack((cmap(np.linspace(.1, .5, 128)),
                                 cmap(np.linspace(.1, .5, 128))[::-1]))

            _colors = np.roll(_colors, int(cmap.N*(-.25)), axis=0)

            cmap = ListedColormap(_colors, name='RdBu_cutted')

            norm = Normalize(vmin=vmin, vmax=vmax, clip=False)

            try:

                contourf += [
                    ax[i].contourf(
                        xx, yy,
                        df.loc[(slice(None), slice(*depth)), variable] \
                            .unstack(level='time').values,  
                        vmin=vmin,
                        vmax=vmax,
                        levels=100,
                        cmap=cmap,
                        norm=norm,
                        extend='both')]

            except TypeError:
                
                contourf += [
                    ax.contourf(
                        xx, yy,
                        df.loc[(slice(None), slice(*depth)), variable] \
                            .unstack(level='time').values,  
                        vmin=vmin,
                        vmax=vmax,
                        levels=100,
                        cmap=cmap,
                        norm=norm,
                        extend='both')]

            cbar_title = 'Direção de Corrente [°]'

        try:

            ax[i].invert_yaxis()
            ax[i].set_ylabel('Profundidade [m]', fontsize=22)
            ax[i].tick_params(axis='y', which='major', labelsize=16)

        except TypeError:

            ax.invert_yaxis()
            ax.set_ylabel('Profundidade [m]', fontsize=22)
            ax.tick_params(axis='y', which='major', labelsize=16)

    # Título
    try:

        ax[0].set_title(
            f'{dataset}\n'
            f'Ponto de grade próximo à {point_name.capitalize()}\n'
            'Diagrama Hovmöller',
            fontsize=22, pad=18)

    except NameError:

        ax[0].set_title(
            f'{dataset}\nPonto de grade próximo à'
            f' lat={round(ds["lat"].item(), ndigits=4)},'
            f' lon={round(ds["lon"].item(), ndigits=4)}\n'
            'Diagrama Hovmöller',
            fontsize=22, pad=18)

    except TypeError:
        
        ax.set_title(
            f'{dataset}\n'
            f'Ponto de grade próximo à {point_name.capitalize()}\n'
            'Diagrama Hovmöller',
            fontsize=22, pad=18)

    cbar = fig.colorbar(
        ScalarMappable(norm=contourf[0].norm, cmap=contourf[0].cmap),
        ax=ax, ticks=ticks, fraction=.015, shrink=.75,
        extend='both')

    cbar.ax.tick_params(labelsize=18, pad=10) 

    cbar.set_label(cbar_title, rotation=270, fontsize=22, labelpad=30)

    month_labels = df[variable].index.get_level_values('time') \
        .unique().strftime('%m/%Y').unique().to_list()

    major_labels = [
        label
        for label in month_labels
        if pd.to_datetime(label, format='%m/%Y').month == 1]

    major_ticks = pd.to_numeric(
        pd.to_datetime(major_labels, format='%m/%Y')).tolist()

    _minor_labels = [
        label
        for label in month_labels
        if pd.to_datetime(label, format='%m/%Y').month in [3, 6, 9, 12]]

    minor_ticks = pd.to_numeric(
        pd.to_datetime(_minor_labels, format='%m/%Y')).tolist()

    minor_labels = [
        dt.strftime('%m')
        for dt in pd.to_datetime(month_labels, format='%m/%Y')
        if dt.month in [3, 6, 9, 12]]

    try:

        ax[-1].set_xticks(
            major_ticks, major_labels, minor=False,
            rotation=90, fontsize=16, ha='center')

        ax[-1].set_xticks(
            minor_ticks, minor_labels, minor=True,
            rotation=90, fontsize=14, ha='center')

    except TypeError:
        
        ax.set_xticks(
            major_ticks, major_labels, minor=False,
            rotation=90, fontsize=16, ha='center')

        ax.set_xticks(
            minor_ticks, minor_labels, minor=True,
            rotation=90, fontsize=14, ha='center')

    try:

        for _ax in ax:

            if _ax == ax[-1]:

                labelbottom = True

            else: 

                labelbottom = False
                
            _ = _ax.tick_params(
                axis='x', which='major', direction='out',
                bottom=True, top=True, labelbottom=labelbottom, labeltop=False,
                width=2, length=8, pad=20)

            _ = _ax.tick_params(
                axis='x', which='minor', direction='out',
                bottom=True, top=True, labelbottom=labelbottom, labeltop=False,
                width=1, length=5)

    except TypeError:
        
        _ = ax.tick_params(
            axis='x', which='major', direction='out',
            bottom=True, top=True, labelbottom=True, labeltop=False,
            width=2, length=8, pad=20)

        _ = ax.tick_params(
            axis='x', which='minor', direction='out',
            bottom=True, top=True, labelbottom=True, labeltop=False,
            width=1, length=5)

    # ax.grid(which='major', color='grey', linestyle='--', linewidth=0.8)

    fig.subplots_adjust(left=.08, right=.87, top=.89, bottom=.13, hspace=.08)

    if clabel:

        cs_plus = ax.contour(
            df[variable].unstack(level='time').values,
            levels=levels, colors='k', linewidths=.2, zorder=3)

        ax.clabel(
            cs_plus, levels,
            fmt='', inline=True, inline_spacing=15, fontsize=10)

        cs_minus = ax.contour(
            df[variable].unstack(level='time').values,
            levels=-levels[::-1], colors='w', linewidths=.2, zorder=3)

        ax.clabel(
            cs_minus, -levels[::-1],
            fmt='', inline=True, inline_spacing=15, fontsize=10)

    fig.savefig(
        f'{path2save}/hovmoller_{variable}_{_depth[0]}-{_depth[-1]}m'
        f'{df.index.get_level_values("time")[0].strftime(r"%b%Y")}'
        f'-{df.index.get_level_values("time")[-1].strftime(r"%b%Y")}_.png',
        format='png')

    return fig, ax


def plot_profile():

    interannual_mean = df[['spd', 'dir']].groupby(
        pd.Grouper(level='depth')).mean()

    interannual_mean['dir'] *= np.nan

    interannual_mean['dir'] = df['dir'].groupby(
        pd.Grouper(level='depth')).apply(
            lambda x: circmean(x, high=360.))

    # Daily Maximum
    
    
    
    # media_mensal = 

    # for depth in ds.depth.values:

    #     media_mensal = df.xs(depth, level='depth').groupby(
    #         pd.Grouper(freq='1M')).mean()

    fig, ax = plt.subplots()

    ax.plot(interannual_mean['spd'], -(interannual_mean.index.values))

    # Move left y-axis to centre
    # ax.spines['left'].set_position('center')

    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')

    ax.set_xlim(0, interannual_mean['spd'].max())
    ax.set_ylim(-interannual_mean.index.values.max(), 100)

    ax.tick_params(
        axis='x', which='major',
        bottom=False, labelbottom=False,
        top=True, labeltop=True)

    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')

    ax.grid(True, color='k', linestyle=':', linewidth=.3)

    ax.set_ylabel('Profundidade [m]', fontsize=12, labelpad=30, rotation=270)

    ax.yaxis.set_label_position('right')

    ax.set_xlabel('Intensidade [m/s]', fontsize=12, labelpad=10)

    ax.xaxis.set_label_position('top')

    # ax.text(
    #     ax.get_xlim()[0],
    #     ax.get_ylim()[0],
    #     f'{ds.time[0].dt.strftime("%d/%m/%Y %Hh").item()}',
    #     bbox=dict(boxstyle='round', facecolor='w', pad=.3),
    #     fontsize=10, fontweight='roman')
    
    fig.savefig(f'{path_local}/perfil.png', format='png')

    return None


if __name__ == '__main__':

    # Mapeamento Contêiner
    path_local = '/rotinas'
    path_data = '/base'
    path2save = '/figuras'

    sys.path.insert(0, f'{path_local}/utils')

    from values import *

    with open(
        '/'.join([path_local, 'input_profile.json'])) as f:

        daux = json.load(f)

    dataset = daux['dataset']             # nome da base de dados
    path_dataset = daux['data_path']      # path dos dados
    start = daux['start']                 # data inicial
    end = daux['end']                     # data final
    year = daux['year']                   # ano específico

    ds = xr.open_mfdataset(f'{path_data}/{path_dataset}/*.nc', autoclose=True)

    ds['spd'], ds['dir'] = uv2spddir(ds['uvel'], ds['vvel'])

    df = ds[['spd', 'dir']].to_dataframe()

    df.drop(['lat', 'lon'], axis=1, inplace=True)

    if any(df['spd'].isna()):

        df.drop(df[df['spd'].isna()].index, inplace=True)



    fig, ax = plt.subplots()
