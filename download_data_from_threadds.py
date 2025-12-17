# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 12/12/2025
# python version:          3


from datetime import datetime
from dateutil.rrule import rrule, DAILY

import requests
from subprocess import call

import pandas as pd
import xarray as xr

import json
import os
import re

import time

# Mapeamento Contêiner
path_data = '/base'
path_local = '/rotinas'

try:

    from utils import dataset_url_prefix

except ModuleNotFoundError:

    import sys

    sys.path.insert(0, path_local)

    from utils import dataset_url_prefix


def download_with_xarray(variables, depth, lon, lat):

    if variables:

        if lon and lat:

            if isinstance(lon, float) and isinstance(lat, float):

                if depth:

                    selected = ds[variables].sel(depth=depth,
                                                 lat=lat,
                                                 lon=lon,
                                                 method='nearest')

                else:

                    selected = ds[variables].sel(lat=lat,
                                                 lon=lon,
                                                 method='nearest')

            elif isinstance(lon, (list, tuple)) and \
                    isinstance(lat, (list, tuple)):

                if depth:

                    selected = ds[variables].sel(depth=depth,
                                                 lat=slice(*lat),
                                                 lon=slice(*lon))

                else:

                    selected = ds[variables].sel(lat=slice(*lat),
                                                 lon=slice(*lon))

        else: 

            if depth:

                selected = ds[variables].sel(depth=depth, method='nearest')

            else:
                
                selected = ds[variables]

    else:

        if lon and lat:

            if isinstance(lon, float) and isinstance(lat, float):

                if depth:

                    selected = ds.sel(depth=depth,
                                    lat=lat,
                                    lon=lon,
                                    method='nearest')

                else:

                    selected = ds.sel(lat=lat,
                                    lon=lon,
                                    method='nearest')

            elif isinstance(lon, (list, tuple)) and \
                    isinstance(lat, (list, tuple)):

                if depth:

                    selected = ds.sel(depth=depth,
                                      lat=slice(*lat),
                                      lon=slice(*lon))

                else:

                    selected = ds.sel(lat=slice(*lat),
                                      lon=slice(*lon))

    # Escrevendo NetCDF
    # kwargs = {encoding={'zlib': True, 'complevel': 9}}

    _ = selected.attrs.pop('_NCProperties', None)

    selected.to_netcdf(
        fpathname, mode='w', format='NETCDF4', engine='netcdf4')

    return None


def write_folder2save():
    """Define nome da pasta onde dados serão salvos,
    se coordenadas forem passadas."""

    _lonlatmin = ''
    _lonlatmax = ''

    if isinstance(lon, (float, int)) and isinstance(lat, (float, int)):

        _lon = f'{round(abs(lon), ndigits=2)}W' if lon < 0 \
                else f'{round(abs(lon), ndigits=2)}E'

        _lat = f'{round(abs(lat), ndigits=2)}S' if lat < 0 \
                else f'{round(abs(lat), ndigits=2)}N'

        _lonlatmin = f'{_lon}_{_lat}'.replace('.', 'o')
        _lonlatmax = ''

    if isinstance(lonLim, list) and isinstance(latLim, list):

        if lonLim and latLim:

            _lonmin = min([float(_lon) for _lon in lonLim])
            _lonmax = max([float(_lon) for _lon in lonLim])

            _latmin = min([float(_lat) for _lat in latLim])
            _latmax = max([float(_lat) for _lat in latLim])

            _lonmin = f'{round(abs(_lonmin), ndigits=2)}W' if _lonmin < 0 \
                    else f'{round(abs(_lonmin), ndigits=2)}E'
            _lonmax = f'{round(abs(_lonmax), ndigits=2)}W' if _lonmax < 0 \
                    else f'{round(abs(_lonmax), ndigits=2)}E'

            _latmin = f'{round(abs(_latmin), ndigits=2)}S' if _latmin < 0 \
                    else f'{round(abs(_latmin), ndigits=2)}N'
            _latmax = f'{round(abs(_latmax), ndigits=2)}S' if _latmax < 0 \
                    else f'{round(abs(_latmax), ndigits=2)}N'

            _lonlatmin = f'{_lonmin}{_latmin}'.replace('.', 'o')
            _lonlatmax = f'_{_lonmax}{_latmax}'.replace('.', 'o')

    return f'{_lonlatmin}{_lonlatmax}'


if __name__ == '__main__':

    with open(
        '/'.join([path_local, 'input_download.json'])) as f:

        daux = json.load(f)

    dataset = daux['dataset']       # nome da base de dados
    start = daux['start']           # data inicial
    end = daux['end']               # data final
    year = daux['year']             # ano específico
    depth = daux['depth']           # profundidade
    lon = daux['lon']               # longitude para um ponto
    lat = daux['lat']               # latitude para um ponto
    lonLim = daux['lonLim']         # limites longitude para um mapa
    latLim = daux['latLim']         # limites latitude para um mapa
    variables = daux['variables']   # lista de variáveis
    folder = daux['folder']         # pasta onde salvar os dados

    # Verificação de lon e lat, devem ser float
    if isinstance(lon, (list, tuple)) or isinstance(lat, (list, tuple)):

        if len(lon) == 1:

            lon, = lon

        if len(lat) == 1:

            lat, = lat

    # Se não for passar uma pasta, cria uma baseada nas coordenadas
    if not folder:

        folder = write_folder2save()

    # Se o diretório não existir, cria
    directory = '/'.join(
        [item
         for item in (path_data, folder, dataset)
         if item])

    if not os.path.exists(directory):

        os.makedirs(directory, exist_ok=True)

    # Período Inicial e Final (datetime)
    _start = datetime.strptime(start, r'%d/%m/%Y %H:%M')
    _end = datetime.strptime(end, r'%d/%m/%Y %H:%M')

    # Endereço, prefixo e sufixo dos arquivos
    url, fprefix, fsuffix = dataset_url_prefix(dataset)

    # Certificar acesso pelo Python
    if re.match('.*(/fileServer/).*', url):

        # dodsC para acessar direto do Python; fileServer para baixar
        url = re.sub('fileServer', 'dodsC', url)

    # Lista de anos do período
    if year:

        _start = _start.replace(year=int(year))

    years = [
        dt.strftime('%Y')
        for dt in pd.date_range(
            str(_start.year), 
            str(_end.year+1),
            freq='YE')]

    log = []

    _now = datetime.now()

    print('Início:', _now)

    for year in years:

        # Período inicial e fina de cada respectivo ano
        start_ = (
            f'{_start.day:02d}/{_start.month:02d}/{year}'
            f' {_start.time().strftime("%H:%M")}')

        end_ = (
            f'{_end.day:02d}/{_end.month:02d}/{year}'
            f' {_end.time().strftime("%H:%M")}')

        # Período em datetime
        dtstart = datetime.strptime(start_, r'%d/%m/%Y %H:%M')
        until = datetime.strptime(end_, r'%d/%m/%Y %H:%M')

        # Arquivos com numeração diária e sequencial ao longo do ano
        # começa em 001
        nday = (dtstart - datetime(int(year), 1, 1, 0, 0)
            ).days + 1

        for i, _ in enumerate(rrule(DAILY, dtstart=dtstart, until=until)):

            fname = f'{fprefix}.{year}_{i+nday:03d}{fsuffix}.nc'

            furl = f'{url}/{year}/{fname}'

            # fpathname = f'{path_data}/{dataset}/{fname}'
            fpathname = '/'.join(
                [item
                 for item in (path_data, folder, dataset, fname)
                 if item])

            # Se o arquivo já existir (ou caso de falha).
            if os.path.isfile(fpathname):

                # Se for maior que 5 kbytes
                if os.path.getsize(fpathname) > 5:

                    print(f'OK: {fname} já baixado')

                    continue

                # Se já houver, não reescreve, salva outro como cópia,
                # portanto precisa apagar o antigo
                else:

                    call(f'rm {fpathname}', shell=True)

                    print(f'Apagado: {fpathname} vazio')

            # Caso contrário, 'baixar' arquivo.
            else:

                try:

                    with xr.open_dataset(furl) as ds:

                        if lon and lat:

                            selected = download_with_xarray(
                                variables, depth, lon, lat)

                        elif lonLim and latLim:

                            selected = download_with_xarray(
                                variables, depth, lonLim, latLim)

                    print('Salvo', fpathname)

                except OSError:

                    print('Não existe', furl)

                    continue

            # Evitar sobrecarga no servidor
            time.sleep(3)

    now = datetime.now()

    print(f'Finalizado em {now}', 'após', str(now - _now))

    # with open(f'/rotinas/{dataset}/download.log', 'w') as f:

    #     f.writelines(log)
