# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 31/07/2025
# python version:          3

'''
Programa para selecionar dados de arquivos e escrever os respectivos dados
selecionados.

A partir do local onde estão os dados (dataset é o caminho onde estão os .nc), 
cada arquivo é lido e os respectivos parâmetros/variáveis (variable) são
selecionados.

Podem ser selecionados para uma área (especificando latLim e lonLim), uma
profundidade (especificando depth), um ponto (especificando lat e lon), para 
un intervalo de data (date) ou para um determinado ano (year).

Os dados são salvos nos caminho passo por path2save.

Esses parâmetros são especificados e passados como entrada pelo arquivo:
input_download_selected.json
'''


from datetime import datetime
from dateutil.rrule import rrule, DAILY

import requests
from subprocess import call

import pandas as pd
import xarray as xr

import os
import sys
import json

from utils import *


# Mapeamento Contêiner
path_local = '/rotinas'
path_base = '/base'


with open(
    '/'.join([path_local, 'input_download_selected.json'])) as f:

    daux = json.load(f)

dataset = daux['dataset']        # pasta dos dados 
lonLim = sorted(daux['lonLim'])  # limite meridional
latLim = sorted(daux['latLim'])  # limite setentrional
lon = daux['lon_point']          # longitude do ponto
lat = daux['lat_point']          # latitude do ponto
date = daux['date']              # data inicial e final
year = daux['year']              # para um ano específico
variable = daux['variable']      # variável para extração
depth = daux['depth']            # profundidade dos dados
path2save = daux['path2save']    # onde salvar arquivos

# Validar valores lon e lat
if isinstance(lon, str) and isinstance(lat, str):

    try:

        lon = eval(lon)
        lat = eval(lat)

    except SyntaxError:
        
        pass

    else:

        if lon == lon_point and lat == lat_point:

            path2save += ''.join(['_', point_name.lower()])

if not os.path.exists(f'{path_base}/{path2save}'):
    
    os.mkdir(f'{path_base}/{path2save}')

if all([not _date for _date in date]) and not year:

    start = '01/08/2010 00:00'
    end = '31/12/2019 23:00'

elif all([_date for _date in date]):
    
    start, end = date
    
elif year and not any([_date for _date in date]):
    
    start, end = datetime(year, 1, 1, 0, 0), datetime(year, 1, 1, 23, 0)

_start = datetime.strptime(start, r'%d/%m/%Y %H:%M')
_end = datetime.strptime(end, r'%d/%m/%Y %H:%M')

fprefix = 'archvhc'

years = [
    dt.strftime('%Y')
    for dt in pd.date_range(
        str(_start.year), str(_end.year+1), freq='YE')]

# log = []

start_ = datetime.now()

print('Início:', start_)

for _year in years:

    s_start = (
        f'{_start.day:02d}/{_start.month:02d}/{_year}'
        f' {_start.time().strftime("%H:%M")}')

    s_end = (
        f'{_end.day:02d}/{_end.month:02d}/{_year}'
        f' {_end.time().strftime("%H:%M")}')

    start = datetime.strptime(s_start, r'%d/%m/%Y %H:%M')
    end = datetime.strptime(s_end, r'%d/%m/%Y %H:%M')

    # Arquivos com numeração diária e sequencial ao longo do ano
    nday = (
        start - datetime(int(_year), 1, 1, 0, 0)
        ).days + 1

    for i, _ in enumerate(rrule(DAILY, dtstart=start, until=end)):

        fname = f'{fprefix}.{_year}_{i+nday:03d}.nc'

        # preciso salvar dentro da pasta dataset em algum momento?
        # fpathname = f'{path_base}/{path2save}/{fname}'

        # Se o arquivo já existir (caso de falha).
        if os.path.isfile(f'{path_base}/{path2save}/{fname}'):

            # E for maior que 0 bytes
            if os.path.getsize(f'{path_base}/{path2save}/{fname}') > 0:

                print(f'{path_base}/{path2save}/{fname}', 'já existe')

                continue

            # Se já houver o arquivo não reescreve, salva outro como cópia,
            # portanto o arquivo vazio é apagado antes
            else:

                call(f'rm {path_base}/{path2save}/{fname}', shell=True)

                print(f'{path_base}/{path2save}/{fname}', 'vazio')

        # Caso contrário, ler o arquivo.
        else:

            try:

                with xr.open_dataset(f'{path_base}/{dataset}/{fname}') as ds:

                    if variable:

                        if depth:

                            selected = ds[variable].sel(
                                depth=depth, lat=lat, lon=lon, method='nearest')

                        else:

                            selected = ds[variable].sel(
                                lat=lat, lon=lon, method='nearest')

                    else:

                        if depth:

                            selected = ds.sel(
                                depth=depth, lat=lat, lon=lon, method='nearest')

                        else:

                            selected = ds.sel(
                                lat=lat, lon=lon, method='nearest')

                # Escrevendo NetCDF
                # kwargs = {encoding={'zlib': True, 'complevel': 9}}

                _ = selected.attrs.pop('_NCProperties', None)

                selected.to_netcdf(
                    f'{path_base}/{path2save}/{fname}',
                    mode='w', format='NETCDF4', engine='netcdf4')

                print('Salvo', f'{path_base}/{path2save}/{fname}')

            except OSError:

                print('Não existe', f'{path_base}/{dataset}/{fname}')

                continue

end_ = datetime.now()

print(f'Finalizado em {end_}', 'após', str(end_-start_))

# with open('/rotinas/download_selected.log', 'w') as f:

#     f.writelines(log)
