
import pandas as pd
from itertools import combinations_with_replacement

# Carregar os dados do arquivo CSV
file_path = './novaes/combination/dados_produto_base.csv'
dados_produto = pd.read_csv(file_path)

def convert_currency_to_float(value):
    return float(value.replace('R$', '').replace(',', '.').strip())

def convert_time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60

def format_product_names(names):
    if len(names) > 1:
        return ', '.join(names[:-1]) + ' e ' + names[-1]
    return names[0]

# Convertendo os dados para formatos adequados
dados_produto['Margem de Contribuição por unidade'] = dados_produto['Margem de Contribuição por unidade'].apply(convert_currency_to_float)
dados_produto['Tempo de produção por receita'] = dados_produto['Tempo de produção por receita'].apply(convert_time_to_minutes)

tempo_maximo_diario = 300  # 5 horas em minutos

todas_combinacoes_validas = []

# Gerar todas as combinações possíveis dos produtos
for i in range(1, len(dados_produto) + 1):
    for comb in combinations_with_replacement(dados_produto.index, i):
        produtos_combinados = dados_produto.loc[list(comb)]
        tempo_total = produtos_combinados['Tempo de produção por receita'].sum()
        
        if tempo_total <= tempo_maximo_diario:
            produtos_nomes = format_product_names(produtos_combinados['Produto'].tolist())
            margem_contribuicao_total = sum(produtos_combinados['Margem de Contribuição por unidade'] * produtos_combinados['Quantidade fabricada por produto'])
            todas_combinacoes_validas.append((produtos_nomes, tempo_total, margem_contribuicao_total))

# Conversão das combinações válidas para DataFrame para visualização ou exportação
df_combinacoes_validas = pd.DataFrame(todas_combinacoes_validas, columns=['Produtos', 'Tempo Total', 'Margem de Contribuição Total'])

print(df_combinacoes_validas)
# Você também pode exportar isso para um arquivo CSV se desejar
# df_combinacoes_validas.to_csv('combinacoes_validas_com_margem.csv', index=False)
df_combinacoes_validas.to_excel('./novaes/combination/combinacoes_possiveis.xlsx', index=False)
