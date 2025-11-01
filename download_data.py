# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 15/01/2025
# python version:          3


from datetime import datetime
from dateutil.rrule import rrule, DAILY

import requests
from subprocess import call

import pandas as pd
# import xarray as xr

import json
import os

# Mapeamento Contêiner
path_data = '/base'
path_local = '/rotinas'

try:
    
    from utils import dataset_url_prefix
    
except ModuleNotFoundError:

    import sys

    sys.path.insert(0, path_local)

    from utils import dataset_url_prefix


with open(
    '/'.join([path_local, 'input_download.json'])) as f:

    daux = json.load(f)

dataset = daux['dataset']             # nome da base de dados
start = daux['start']                 # data inicial
end = daux['end']                     # data final
year = daux['year']                   # ano específico

# Datas auxiliares
_start = datetime.strptime(start, r'%d/%m/%Y %H:%M')
_end = datetime.strptime(end, r'%d/%m/%Y %H:%M')

url, fprefix, fsuffix = dataset_url_prefix(dataset)

if not year:

    years = [
        dt.strftime('%Y')
        for dt in pd.date_range(
            str(_start.year), 
            str(_end.year+1),
            freq='YE')]

log = []

start_ = datetime.now()

print('Início:', start_)

for year in years:
# for year in ['2010', '2011', '2012', '2013', '2014',
#              '2015', '2017', '2018', '2019']:

    s_start = (
        f'{_start.day:02d}/{_start.month:02d}/{year}'
        f' {_start.time().strftime("%H:%M")}')

    s_end = (
        f'{_end.day:02d}/{_end.month:02d}/{year}'
        f' {_end.time().strftime("%H:%M")}')
    
    start = datetime.strptime(s_start, r'%d/%m/%Y %H:%M')
    end = datetime.strptime(s_end, r'%d/%m/%Y %H:%M')

    # Arquivos com numeração diária e sequencial ao longo do ano
    # começa em 001
    nday = (start - datetime(int(year), 1, 1, 0, 0)
        ).days + 1

    for i, _ in enumerate(rrule(DAILY, dtstart=start, until=end)):

        fname = f'{fprefix}.{year}_{i+nday:03d}{fsuffix}.nc'

        fpathname = f'{path_data}/{dataset}/{fname}'

        # Se o arquivo já existir (ou caso de falha).
        if os.path.isfile(fpathname):

            if os.path.getsize(fpathname) > 0:

                print(f'OK: {fname} já baixado')

                continue

            # Se já houver o arquivo não sobreescreve, 
            # salva outro como cópia, então apagando o vazio
            elif os.path.getsize(fpathname) == 0: 

                call(f'rm {fpathname}', shell=True)

                cmd = f'wget -q -P {path_data}/{dataset}/ {url}/{year}/{fname}'

                call(cmd, shell=True)

                print(f'OK: {fname} baixado')

        # Caso contrário, baixar arquivo.
        else:

            response = requests.head(f'{url}/{year}/{fname}')

            # Se o arquivo não existir: status = NOK
            if not response.status_code == requests.codes.ok:

                print(f'NOK: Não existe {url}/{year}/{fname}')

                continue

            cmd = f'wget -q -P {path_data}/{dataset}/ {url}/{year}/{fname}'

            call(cmd, shell=True)

            print(f'OK: {fname} baixado')

end_ = datetime.now()

print(f'Finalizado em {end_}', 'após', str(end_-start_))

# with open('/rotinas/download.log', 'w') as f:

#     f.writelines(log)
