''' Teste para modularização
    Criado: 28/10/2025 '''

# Aqui ao invés de importar diretamente da pasta
# from teste.teste_math import func_math
# from teste.teste_string import func_string

# Importar pelo atalho de __init__.py
from teste import func_math, func_string, uma_string


if __name__ == '__main__':

    print('teste importação')

    print(func_math(2, 3))

    print(func_string('a', 'b'))

    print(uma_string)