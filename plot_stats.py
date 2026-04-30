# -*- coding: utf-8 -*-
# author (unless omitted): Ronaldo Mitsuo Sato
# email:                   ronaldo.sato@gmail.com
# created:                 23/03/2026
# python version:          3

import json
from math import trunc, floor, ceil
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import re
import warnings

# import sys

# sys.path.insert(0, '/rotinas')

# from utils import


def truncate_value(x, kind='trunc', decimals=0):
    """
    Aplica o truncamento ou arredondamento a um valor numérico.

    O comportamento é determinado pelo tipo de operação escolhida 
    e pela precisão de casas decimais especificada pelo usuário.

    Args:
        x (float): O valor numérico a ser processado.
        kind (str, optional): O tipo de operação a ser realizada. 
            Pode ser 'trunc' (truncar), 'floor' (arredondar para baixo) 
            ou 'ceil' (arredondar para cima). O padrão é 'trunc'.
        decimals (int, optional): O número de casas decimais a serem 
            mantidas no resultado. O padrão é 0.

    Returns:
        float: O valor resultante após a aplicação do fator de escala e 
            da operação matemática correspondente.
    """
    factor = float(10**decimals)

    if kind == 'trunc':

        return trunc(x*factor) / factor

    elif kind == 'floor':

        return floor(x*factor) / factor

    elif kind == 'ceil':

        return ceil(x*factor) / factor


def stats_ordered_by_month(
        stats,
        keys=['mean', 'median', 'std'],
        months=['Jan', 'Fev', 'Mar', 'Abr',
                'Mai', 'Jun', 'Jul', 'Ago',
                'Set', 'Out', 'Nov', 'Dez']):
    """
    Reorganiza dicionário de estatísticas estruturado por profundidade 
    para um formato por mês.

    A função agrupa os valores de diferentes métricas (respectivamente 
    declaradas por keys) associando-os aos meses correspondentes, 
    percorrendo as chaves de profundidade dentro do dicionário original.

    Args:
        stats (dict): Dicionário aninhado contendo as métricas 
            (ex: stats['mean'][profundidade]).
        keys (list, optional): Lista de chaves métricas a serem 
            processadas. Padrão: ['mean', 'median', 'std'].
        months (list, optional): Lista com os nomes dos meses na ordem
            dos dados. Padrão são as abreviações do meses em português.

    Returns:
        dict: Um novo dicionário onde o primeiro nível são as métricas 
            (keys) e o segundo nível são os meses, contendo listas de 
            valores de todas as profundidades.
    """
    _stats = {}

    for key in keys:

        _stats[key] = {}

        for i, month in enumerate(months):

            _stats[key][month] = [
                stats[key][depth][i]
                for depth in stats[key].keys()
            ]

    return _stats


def get_max_min_values(stats):
    """
    Calcula os valores mínimo e máximo baseados na média e 
    desvio padrão.

    A função percorre um dicionário de estatísticas mensais, 
    subtraindo o desvio padrão da média para encontrar o limite inferior
    e somando-os para o limite superior.

    Args:
        stats (dict): Um dicionário contendo as chaves 'mean' e 'std'. 
            Cada chave deve mapear para outro dicionário onde os valores
            são listas de números (ex: {month: [valores]}).

    Returns:
        tuple: Uma tupla contendo (_min, _max), representando o menor 
        valor da (média - desvio) e o maior valor da (média + desvio) 
        encontrados.
    """

    try:

        mean_values = [item
                       for month in stats['mean'].keys()
                       for item in stats['mean'][month]
                       ]

        std_values = [item
                      for month in stats['std'].keys()
                      for item in stats['std'][month]
                      ]

    except TypeError:

        mean_values = [stats['mean'][depth]
                       for depth in stats['mean'].keys()]

        std_values = [stats['std'][depth]
                      for depth in stats['std'].keys()]

    _min = min(list(map(lambda x, y: x - y,
                        mean_values,
                        std_values
                        )
                    )
               )

    _max = max(list(map(lambda x, y: x + y,
                        mean_values,
                        std_values
                        )
                    )
               )

    return (_min, _max)


def plot_variable_monthy_stats_series():
    """
    Gera o gráfico da estatística mensal para uma variável específica.

    A visualização inclui curvas de máximo, mínimo, média, mediana e as
    faixas de desvio padrão (abaixo e acima da média). O comportamento 
    do gráfico é determinado pelas variáveis de contexto globais 
    (stats, depth e variable).

    Returns:
        tuple: Uma tupla contendo os objetos (fig, ax) do Matplotlib 
            para customizações adicionais ou exibição.

    Note:
        Esta função depende de variáveis globais previamente definidas:
        - `stats`: Dicionário com os dados processados.
        - `depth`: A profundidade específica a ser plotada.
        - `variable`: O identificador da variável atual.
        - `variable_name`: Dicionário para mapeamento do rótulo do eixo Y.
        - `num_month`: Dicionário para conversão de índices em nomes de meses.
    """
    fig, ax = plt.subplots(figsize=(18, 14))

    kw_plot = dict(
        marker='o', markersize=3, linestyle='-', linewidth=.8)

    ax.plot(
        stats['MONTHS'], stats['max'][depth],
        color='r', label='Máximo', **kw_plot)

    ax.plot(
        stats['MONTHS'],
        list(map(lambda x, y: x + y,
                 stats['mean'][depth], stats['std'][depth])),
        color='y', label='Média + Desvio Padrão', **kw_plot)

    ax.plot(
        stats['MONTHS'], stats['mean'][depth],
        color='b', label='Média', **kw_plot)

    ax.plot(
        stats['MONTHS'], stats['median'][depth],
        color='g', label='Mediana', **kw_plot)

    ax.plot(
        stats['MONTHS'],
        list(map(lambda x, y: x - y,
                 stats['mean'][depth], stats['std'][depth])),
        color='y', label='Média - Desvio Padrão', **kw_plot)

    ax.plot(
        stats['MONTHS'], stats['min'][depth],
        color='r', label='Mínimo',  **kw_plot)

    ax.legend(
        loc='center right',
        bbox_to_anchor=(.998, .5),
        bbox_transform=fig.transFigure,
        fontsize=16)

    ax.grid(axis='both', linestyle=':', linewidth=.6, zorder=0)

    fig.subplots_adjust(left=.07, top=.92, right=.8, bottom=.07)

    kw_label = dict(fontsize=24)

    ax.set_title(
        'Área Sísmica - Valores Estatísticos Mensais',
        pad=20, **kw_label)

    ax.set_ylabel(
        variable_name[variable], fontweight='semibold', **kw_label)

    ax.set_xlabel('')

    ticks = list(range(1, 13, 2))
    minor_ticks = list(range(2, 13, 2))

    months = [num_month[str(num)] for num in ticks]

    _ = ax.set_xticks(ticks)
    _ = ax.set_xticks(minor_ticks, minor=True)
    _ = ax.set_xticklabels(months)

    ax.tick_params(axis='both', which='major', labelsize=18)

    return fig, ax


def plot_profile_subplots():
    """
    Gera subplots (nrows X ncols) de perfis verticais da estatística 
    mensal, onde cada subplot representa um mês.

    Cada subplot exibe a variação do valores estatísticos da variável 
    em relação à profundidade. 

    Os limites dos eixos X são normalizados globalmente e o eixo Y é 
    invertido para representar a profundidade.

    Returns:
        tuple: Uma tupla contendo os objetos (fig, ax) do Matplotlib.

    Note:
        Esta função depende de diversas variáveis e funções de suporte 
        do escopo global:

        - `stats` e `stats_bymonth`: Dicionários com os dados brutos e
            processados por mês.
        - `variable` e `variable_name`: Identificadores para os títulos 
            e rótulos.
        - `num_month`: Dicionário de tradução para os nomes dos meses.
        - `get_max_min_values` e `truncate_value`: Funções auxiliares 
            para escala dos eixos.
    """
    kw_plot = dict(
        marker='o', markersize=2, linestyle='-', linewidth=.8)

    ncols = len(stats['MONTHS']) // 2
    nrows = (len(stats['MONTHS']) // ncols) + \
            (len(stats['MONTHS']) % ncols)

    fig, ax = plt.subplots(nrows=nrows,
                           ncols=ncols,
                           figsize=(22, 18))

    fig.suptitle(
        f'{prefix_title} - Valores Estatísticos Mensais\n' +
        f'$\\mathbf{{{variable_name[variable]}}}$',
        fontsize=24, linespacing=1.6)

    depths = stats['DEPTHS']

    xmin, xmax = get_max_min_values(stats_bymonth)

    xmin = truncate_value(xmin, kind='floor', decimals=1)
    xmax = truncate_value(xmax, kind='ceil', decimals=1)

    num = 0

    for row, _ in enumerate(ax):

        for col, _ in enumerate(ax[row]):

            num += 1
            month = num_month[str(num)]

            ax[row][col].set_xlim(xmin, xmax)

            ax[row][col].invert_yaxis()

            ax[row][col].tick_params(
                axis='x', which='major',
                bottom=False, labelbottom=False,
                top=True, labeltop=True, labelsize=18)

            ax[row][col].tick_params(
                axis='y', which='major', labelsize=18)

            ax[row][col].spines['right'].set_color('none')
            ax[row][col].spines['bottom'].set_color('none')

            ax[row][col].grid(
                True, color='k', linestyle=':', linewidth=.3)

            if variable in ['spd', 'saln']:

                ax[row][col].xaxis.set_minor_locator(
                    MultipleLocator(.1))

            elif variable in ['temp']:

                ax[row][col].xaxis.set_minor_locator(
                    MultipleLocator(1))

            ax[row][col].tick_params(
                axis='x', which='minor',
                bottom=False, labelbottom=False,
                top=True, labeltop=False)

            if col == 0:

                ax[row][col].set_ylabel(
                    'Profundidade [m]',
                    fontsize=24, labelpad=15, rotation=90)

            ax[row][col].set_xlabel(
                month, fontsize=22, labelpad=20)

            # ax[row][col].set_title(
            #     variable_name[variable], fontsize=18, pad=20)

            ax[row][col].xaxis.set_label_position('top')

            ax[row][col].plot(
                list(
                    map(lambda x, y: x - y,
                        stats_bymonth['mean'][month],
                        stats_bymonth['std'][month])),
                depths,
                color='y', label='Média - Desvio Padrão', **kw_plot)

            ax[row][col].plot(
                stats_bymonth['mean'][month],
                depths,
                color='b', label='Média', **kw_plot)

            ax[row][col].plot(
                stats_bymonth['median'][month],
                depths,
                color='g', label='Mediana', **kw_plot)

            ax[row][col].plot(
                list(
                    map(lambda x, y: x + y,
                        stats_bymonth['mean'][month],
                        stats_bymonth['std'][month])),
                depths,
                color='y', label='Média + Desvio Padrão', **kw_plot)

            if month == 'Dez':

                ax[row][col].legend(
                    loc='upper right',
                    bbox_to_anchor=(.98, .99),
                    bbox_transform=fig.transFigure,
                    fontsize=18)

            fig.subplots_adjust(
                left=.075, right=.98, top=.835, bottom=.04,
                wspace=.25, hspace=.15)

    return fig, ax


def plot_profile():

    fig, ax = plt.subplots(figsize=(18, 14))

    kw_plot = dict(
        marker='o', markersize=3, linestyle='-', linewidth=.8)

    xmin, xmax = get_max_min_values(stats[variable])

    ax.set_xlim(
        truncate_value(xmin, kind='floor', decimals=1),
        truncate_value(xmax, kind='ceil', decimals=1))

    ax.set_ylim(
        min(float(depth) for depth in stats[variable]['min'].keys()),
        max(float(depth) for depth in stats[variable]['max'].keys()))

    # ax.spines['left'].set_position('data')
    # ax.spines['bottom'].set_position('zero')

    ax.invert_yaxis()

    ax.tick_params(
        axis='x', which='major',
        bottom=False, labelbottom=False,
        top=True, labeltop=True)

    ax.tick_params(axis='both', which='major', labelsize=18)

    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')

    ax.grid(True, color='k', linestyle=':', linewidth=.3)

    ax.set_ylabel(
        'Profundidade [m]', fontsize=24, labelpad=15, rotation=90)

    ax.set_xlabel(
        f'$\\mathbf{{{variable_name[variable]}}}$',
        fontsize=24, labelpad=20)

    ax.xaxis.set_label_position('top')

    kw_plot = dict(
        marker='o', markersize=2, linestyle='-', linewidth=.8)

    # ax.plot(
    #     stats[variable]['min'].values(),
    #     [float(depth) for depth in stats[variable]['min'].keys()],
    #     color='r', label='Mínimo', **kw_plot)

    ax.plot(
        list(
            map(
                lambda x, y: x - y,
                stats[variable]['mean'].values(),
                stats[variable]['std'].values())),
        [float(depth) for depth in stats[variable]['min'].keys()],
        color='y', label='Média - Desvio Padrão', **kw_plot)

    ax.plot(
        stats[variable]['median'].values(),
        [float(depth) for depth in stats[variable]['min'].keys()],
        color='g', label='Mediana', **kw_plot)

    ax.plot(
        stats[variable]['mean'].values(),
        [float(depth) for depth in stats[variable]['min'].keys()],
        color='b', label='Média', **kw_plot)

    ax.plot(
        list(
            map(
                lambda x, y: x + y,
                stats[variable]['mean'].values(),
                stats[variable]['std'].values())),
        [float(depth) for depth in stats[variable]['min'].keys()],
        color='y', label='Média + Desvio Padrão', **kw_plot)

    # ax.plot(
    #     stats[variable]['max'].values(),
    #     [float(depth) for depth in stats[variable]['min'].keys()],
    #     color='r', label='Máximo', **kw_plot)

    ax.legend(
        loc='center right',
        bbox_to_anchor=(.99, .5),
        bbox_transform=fig.transFigure,
        fontsize=16)

    fig.subplots_adjust(left=.09, right=.82, bottom=.08)

    kw_label = dict(fontsize=24)

    ax.set_title(
        'Área Sísmica - Valores Estatísticos Mensais',
        pad=20, **kw_label)

    if False:
        # Plotar macarrões
        ...

    return fig, ax


def stats_as_array(simple_dict, depths=[]):
    """
    Converte os valores de um dicionário que armazena valores 
    estatísticos em um array NumPy multidimensional.

    A função extrai as listas ou sequências contidas em cada chave do
    dicionário fornecido e as organiza em uma estrutura de matriz.

    Caso uma lista de profundidades seja especificada, apenas as chaves
    correspondentes serão incluídas no array resultante.

    Args:
        simple_dict (dict): Dicionário onde cada chave mapeia uma lista 
            de valores numéricos (ex: dados por mês ou profundidade),
            cujos valores são concatenados verticalmente.
        depths (list, optional): Lista de chaves (profundidades) para filtrar 
            o dicionário. Se estiver vazia, todos os itens são processados. 
            O padrão é [].

    Returns:
        numpy.ndarray: Um array bidimensional contendo os valores 
            extraídos (removendo as chaves originais). A ordem das 
            linhas é determinada pela ordem de iteração do dicionário 
            (já é escrito ordenado) ou pela filtragem das chaves.
    """
    if not all(isinstance(depth, str) for depth in depths):

        depths = [str(float(depth)) for depth in depths]

    if not depths:

        return np.array([values for _, values in simple_dict.items()])

    else:

        return np.array(
            [values
             for key, values in simple_dict.items()
             if key in depths])


def make_ticks(start, stop, n_values=10, step=.05):
    """
    Gera uma sequência de marcadores (ticks) com espaçamento dinâmico.

    O intervalo entre os valores é inicialmente definido por um 
    passo base e incrementado progressivamente até que a quantidade 
    total de marcadores  seja inferior ou igual ao limite especificado.

    Args:
        start (float): O valor inicial do intervalo (inclusive).
        stop (float): O valor final do intervalo (exclusive).
        n_values (int, optional): O número máximo de marcadores desejados 
            no resultado final. O padrão é 10.
        step (float, optional): O incremento inicial fornecido para o 
            espaçamento entre os ticks. O padrão é 0.05.

    Returns:
        numpy.ndarray: Um array contendo os valores dos marcadores 
            determinados pelo algoritmo de ajuste de escala.
    """
    ticks = np.arange(start, stop, step)

    i = 1

    while not ticks.size <= n_values:

        ticks = np.arange(start, stop, step*i)

        i += 1

    return ticks


def get_figsize(n_months, n_depths, total_months, total_depths):
    """
    Calcula as dimensões proporcionais de uma figura com base na 
    "densidade" de dados (linhas e colunas).

    A função determina a largura e altura ideais para o gráfico, 
    permitindo que os argumentos sejam fornecidos tanto como valores 
    inteiros (contagem) quanto como objetos iteráveis (listas ou
    arrays), dos quais o comprimento será extraído.

    Args:
        n_months (int ou list): Quantidade de meses selecionados para
            o gráfico atual ou a lista contendo esses meses.
        n_depths (int ou list): Quantidade de profundidades selecionadas
            para o gráfico atual ou a lista contendo essas 
            profundidades.
        total_months (int ou list): Total de meses disponíveis no 
            conjunto de dados ou a lista completa de meses.
        total_depths (int ou list): Total de profundidades disponíveis
            no conjunto de dados ou a lista completa de profundidades.

    Returns:
        tuple: Uma tupla (largura, altura) em polegadas, calculada para
            manter a proporção visual adequada na plotagem.
    """
    if not isinstance(n_months, int):

        n_months = len(n_months)

    if not isinstance(n_depths, int):

        n_depths = len(n_depths)

    if not isinstance(total_months, int):

        total_months = len(total_months)

    if not isinstance(total_depths, int):

        total_depths = len(total_depths)

    return (12 * n_months) / total_months, \
           ((20 * n_depths) / total_depths) * 1.25


def plot_heatmap(key, cmap, depths=[]):
    """
    Gera um mapa de calor (heatmap) para uma métrica estatística 
    específica.

    A figura correlaciona meses e profundidades, aplicando anotações
    numéricas em cada célula. A escala de cores e os marcadores da barra
    de cores são determinados automaticamente com base na variável
    global ativa e nos limites globais dos dados.

    Args:
        key (str): A métrica a ser visualizada (ex: 'mean', 'median', 
            'std', 'mean+std' ou 'mean-std').
        cmap (str ou Colormap): O mapa de cores do Matplotlib fornecido
            para a representação dos valores.
        depths (list, optional): Lista de profundidades para filtrar 
            o eixo Y. Se estiver vazia, são utilizadas as profundidades
            estabelecidas no dicionário global 'stats'. O padrão é [].

    Returns:
        tuple: Uma tupla contendo os objetos (fig, ax) do Matplotlib.

    Note:
        Esta função depende de um conjunto robusto de dependências 
        globais:
            - Funções: `fig_size`, `get_max_min_values`, 
                `stats_as_array`, `make_ticks` e `truncate_value`.
            - Variáveis: `stats`, `variable`, `variable_name`, 
                `stats_nome` e `num_month`.
    """
    if not depths:

        depths = stats['DEPTHS']

    months = stats['MONTHS']

    # fig, ax = plt.subplots(figsize=(12, 20))

    # Proporção da figura a partir das colunas e linhas
    fig, ax = plt.subplots(
        figsize=get_figsize(len(months),
                            len(depths),
                            len(stats['MONTHS']),
                            len(stats['DEPTHS'])
                            )
    )

    vmin, vmax = get_max_min_values(stats)

    if key == 'mean+std':

        data = stats_as_array(stats['mean'], depths=depths) + \
            stats_as_array(stats['std'], depths=depths)

    elif key == 'mean-std':

        data = stats_as_array(stats['mean'], depths=depths) - \
            stats_as_array(stats['std'], depths=depths)

    else:

        data = stats_as_array(stats[key], depths=depths)

    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)

    # Position: [left, bottom, width, height] in figure coordinates
    cax = fig.add_axes([.82, .25, .02, .5])

    if variable == 'spd':

        ticks = make_ticks(
            truncate_value(vmin, kind='floor', decimals=1),
            truncate_value(vmax, kind='floor', decimals=1),
            step=.01, n_values=15)

    elif variable == 'temp':

        ticks = make_ticks(
            truncate_value(vmin, kind='floor', decimals=1),
            truncate_value(vmax, kind='floor', decimals=1),
            step=.06, n_values=13)

    else:

        ticks = make_ticks(
            truncate_value(vmin, kind='floor', decimals=1),
            truncate_value(vmax, kind='floor', decimals=1))

    cbar = ax.figure.colorbar(
        im, cax=cax, shrink=.8, extend='both', ticks=ticks)

    cbar.ax.tick_params(labelsize=18)

    cbar.ax.set_ylabel(
        f'{stats_nome[key]}: {variable_name[variable]}',
        rotation=-90, va='bottom', fontsize=24, labelpad=15)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(
        range(len(months)),
        labels=[num_month[str(month)] for month in months],
        rotation=45, ha='right', rotation_mode='anchor')

    ax.set_yticks(
        range(len(depths)),
        labels=[str(int(float(depth))) for depth in depths])

    # Loop over data dimensions and create text annotations.
    for i in range(len(depths)):
        for j in range(len(months)):
            text = ax.text(
                j, i, np.round(data[i, j], decimals=1),
                ha='center', va='center',
                color='w', fontweight='semibold', fontsize=13)

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which='minor', color='w', linestyle='-', linewidth=3)
    ax.tick_params(which='minor', bottom=False, left=False)

    fig.suptitle(
        f'{prefix_title} - Valores Estatísticos Mensais\n',
        y=.98, fontsize=26)

    ax.set_title(
        f'{variable_name[variable]}: {stats_nome[key]}',
        fontsize=26, pad=20, fontweight='semibold')

    ax.tick_params(axis='x', which='major', labelsize=20)
    ax.tick_params(axis='y', which='major', labelsize=18)

    ax.set_xlabel('')
    ax.set_ylabel(
        'Profundidade [m]', fontsize=24, fontweight='semibold')

    # fig.subplots_adjust(left=.01, right=.9, top=.92, bottom=.05)
    fig.tight_layout()

    return fig, ax


def plot_heatmap_subplots(
        keys=['min', 'mean-std', 'mean', 'mean+std', 'max'],
        depths=[]):

    import matplotlib.patches as mpatches

    if not depths:

        depths = stats['DEPTHS']

    months = stats['MONTHS']

    vmin = min(
        [values
         for depth in stats['min'].keys()
         for values in stats['min'][depth]])

    vmax = max(
        [values
         for depth in stats['max'].keys()
         for values in stats['max'][depth]])

    # figsize=(26, 14)

    fig, ax = plt.subplots(
        nrows=1, ncols=len(keys), figsize=(20, 8))

    fig.suptitle(
        f'{prefix_title} - Valores Estatísticos Mensais\n' +
        f'$\\mathbf{{{variable_name[variable]}}}$',
        y=.98, fontsize=26)

    for key, _ax in zip(keys, ax):

        if key == 'mean+std':

            data = stats_as_array(stats['mean'], depths=depths) + \
                stats_as_array(stats['std'], depths=depths)

        elif key == 'mean-std':

            data = stats_as_array(stats['mean'], depths=depths) - \
                stats_as_array(stats['std'], depths=depths)

        else:

            data = stats_as_array(stats[key], depths=depths)

        im = _ax.imshow(
            data, cmap=cmaps[variable], vmin=vmin, vmax=vmax)

        if key == keys[-1]:

            # Position: [left, bottom, width, height] in figure coordinates
            cax = fig.add_axes([.93, .25, .01, .5])

            if variable == 'spd':

                ticks = make_ticks(
                    truncate_value(vmin, kind='floor', decimals=1),
                    truncate_value(vmax, kind='floor', decimals=1),
                    step=.01, n_values=10)  # n_values=15

            elif variable == 'temp':

                ticks = make_ticks(
                    truncate_value(vmin, kind='floor', decimals=1),
                    truncate_value(vmax, kind='floor', decimals=1),
                    step=.06, n_values=8)  # n_values=13

            else:

                ticks = make_ticks(
                    truncate_value(vmin, kind='floor', decimals=1),
                    truncate_value(vmax, kind='floor', decimals=1))

            cbar = _ax.figure.colorbar(
                im, cax=cax, shrink=.8, extend='both')  # , ticks=ticks)

            cbar.ax.tick_params(labelsize=18)

            cbar.ax.set_ylabel(
                f'{variable_name[variable]}',
                rotation=-90, va='bottom', fontsize=24, labelpad=15)

            labels = [
                r'$\mu$ - Média',
                r'$\sigma$ - Desv. Padrão',
                r'$x_{\mathrm{max}}$ - Máximo',
                r'$x_{\mathrm{min}}$ - Mínimo',
            ]

            handles = [
                mpatches.Patch(
                    facecolor=None, edgecolor=None, label=label)
                for label in labels]

            _ax.legend(
                handles=handles,
                loc='upper right',
                bbox_to_anchor=(.995, .995),
                bbox_transform=fig.transFigure,
                fontsize=16,
                handlelength=0,   # largura do ícone
                handletextpad=0,  # espaço entre ícone e texto
                labelspacing=.3,  # diminuir o espaço vertical
            )

        _ax.set_xticks(
            range(len(months)),
            labels=[num_month[str(month)] for month in months],
            rotation=60, ha='right', rotation_mode='anchor')

        if key == keys[0]:

            _ax.set_yticks(
                range(len(depths)),
                labels=[str(int(float(depth))) for depth in depths])

        else:

            _ax.set_yticks(
                range(len(depths)),
                labels=[''] * len(depths))

        # Loop over data dimensions and create text annotations.
        # for i in range(len(depths)):
        #     for j in range(len(months)):
        #         text = _ax.text(
        #             j, i, np.round(data[i, j], decimals=1),
        #             ha='center', va='center',
        #             color='w', fontweight='semibold', fontsize=13)

        # Turn spines off and create white grid.
        # _ax.spines[:].set_visible(False)

        _ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
        _ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
        _ax.grid(which='minor', color='w', linestyle='-', linewidth=.7)
        _ax.tick_params(which='minor', bottom=False, left=False)

        _ax.set_title(
            f'{title_abrev[key]}',
            fontsize=26, pad=20, fontweight='semibold')

        _ax.tick_params(axis='x', which='major', labelsize=18)
        _ax.tick_params(axis='y', which='major', labelsize=20)

        _ax.set_xlabel('')

        if key == keys[0]:

            _ax.set_ylabel(
                'Profundidade [m]', fontsize=24, fontweight='semibold')

    fig.subplots_adjust(
        left=.08, right=.91, top=.87, bottom=.09, wspace=.03)
        # left=.06, right=.92, top=.87, bottom=.09, wspace=.02)

    # fig.tight_layout()

    return fig, ax


warnings.filterwarnings('ignore')

# Converter Referência Variável em Nome
variable_name = {
    'spd': 'Intensidade [m/s]',
    'saln': 'Salinidade [-]',
    'temp': 'Temperatura [°C]'
}

# Converter Números em Nome de Meses
num_month = {
    '1': 'Jan',
    '2': 'Fev',
    '3': 'Mar',
    '4': 'Abr',
    '5': 'Mai',
    '6': 'Jun',
    '7': 'Jul',
    '8': 'Ago',
    '9': 'Set',
    '10': 'Out',
    '11': 'Nov',
    '12': 'Dez',
}

stats_nome = {
    'mean': 'Média',
    'mean-std': 'Média - Desvio Padrão',
    'mean+std': 'Média + Desvio Padrão',
    'std': 'Desvio Padrão',
    'median': 'Mediana',
    'max': 'Máximo',
    'min': 'Mínimo',
    'quartile': 'Quartil'
}

cmaps = {
    'saln': 'viridis',
    'spd': 'summer',
    'temp': 'plasma',
}

title_abrev = {
    'mean-std': '$\\mu - \\sigma$',
    'mean+std': '$\\mu + \\sigma$',
    'std': '$\\sigma$',
    'mean': '$\\mu$',
    'max': '$x_{\\mathrm{max}}$',
    'min': '$x_{\\mathrm{min}}$',
}

# Mapemanto Contêiner
path_rotinas = '/rotinas'
path_figuras = '/figuras'


if __name__ == '__main__':

    with open(
            '/'.join([path_rotinas, 'input_plot_stats.json'])) as f:

        daux = json.load(f)

    dataset = daux['dataset']
    variable = daux['variable']
    depth = daux['depth_stat']
    depths = daux['depths_plot']
    kind_stats = daux['kind_stats']
    prefix = daux['stats_file_prefix']
    prefix_title = daux['prefix_fig_title']

    # for kind in kind_stats:

    # ESTATÍSTICA AGRUPADA

    if kind_stats:

        # Chaves em stats (dicionário) são str de float
        if isinstance(depth, (int, float)):

            depth = str(float(depth))

        elif isinstance(depth, str):

            depth = str(float(depth))

        # Chaves em dicionário (.json) são strings
        if not all(isinstance(_depth, str) for _depth in depths):

            # em stats são str de float
            depths = [str(float(_depth)) for _depth in depths]

        # Arquivos com "_"
        if not re.search('_', prefix):

            fname = f'{prefix}_{variable}_{kind_stats}_stats.json'

        else:

            fname = f'{prefix}{variable}_{kind_stats}_stats.json'

        fname = f'{path_rotinas}/{fname}'

        with open(fname, 'r') as f:

            stats = json.load(f)

        # PLOT ESTATÍSTICA AGRUPADA

        fig, ax = plot_variable_monthy_stats_series()

        fig.savefig(
            f'{path_figuras}/' +
            f'{prefix}_stats_{kind_stats}_' +
            f'series_{variable}_{int(float(depth))}m.png',
            format='png')

        # PLOT HEATMAP

        for i, key in enumerate(['mean', 'mean-std', 'mean+std']):

            _fig, _ = plot_heatmap(
                key=key, cmap=cmaps[variable], depths=depths)

            if depths:

                _fig.savefig(
                    f'{path_figuras}/' +
                    f'{prefix}_stats_{kind_stats}_{variable}' +
                    f'_heatmap_{key}_depths.png',
                    format='png')

            else:

                _fig.savefig(
                    f'{path_figuras}/' +
                    f'{prefix}_stats_{kind_stats}_{variable}' +
                    f'_heatmap_{key}.png',
                    format='png')

        # SUBPLOTS HEATMAP

        fig, ax = plot_heatmap_subplots(depths=depths)

        if depths:

            fig.savefig(
                f'{path_figuras}/' +
                f'_{prefix}_stats_{kind_stats}_{variable}' +
                '_heatmap_subplots_depths.png',
                format='png')

        else:

            fig.savefig(
                f'{path_figuras}/' +
                f'_{prefix}_stats_{kind_stats}_{variable}' +
                '_heatmap_subplots.png',
                format='png')

        # FIGURA SUBPLOTS DOS AGRUPAMENTOS

        stats_bymonth = stats_ordered_by_month(stats)

        fig, _ = plot_profile_subplots()

        fig.savefig(
            f'{path_figuras}/' +
            f'{prefix}_stats_{kind_stats}_profiles_{variable}.png',
            format='png')

    # ESTATÍSTICA GERAL (PERÍODO COMPLETO)

    # Arquivos com "_"
    if not re.search('_', prefix):

        fname = f'{prefix}_{variable}_stats.json'

    else:

        fname = f'{prefix}{variable}_stats.json'

    fname = f'{path_rotinas}/{fname}'

    with open(fname, 'r') as f:

        stats = json.load(f)

    # PLOT ESTATÍSTICA GERAL (PERÍODO COMPLETO)

    fig, _ = plot_profile()

    fig.savefig(
        f'{path_figuras}/{prefix}_stats_profile_{variable}.png',
        format='png')
