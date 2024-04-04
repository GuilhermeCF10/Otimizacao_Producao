import pandas as pd
from itertools import combinations_with_replacement
import matplotlib.pyplot as plt

# Carregar os dados do arquivo CSV
file_path = 'dados_produto_base.csv'  # Substitua pelo caminho correto do seu arquivo local
dados_produto = pd.read_csv(file_path)

def convert_currency_to_float(value):
    return float(value.replace('R$', '').replace(',', '.'))

def convert_time_to_minutes(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60

dados_produto['Margem de Contribuição por unidade'] = dados_produto['Margem de Contribuição por unidade'].apply(convert_currency_to_float)
dados_produto['Tempo de produção por receita'] = dados_produto['Tempo de produção por receita'].apply(convert_time_to_minutes)

tempo_maximo_diario = 5 * 60  # 5 horas em minutos
dias_de_producao = 10
demanda_restante = dados_produto['Vendas para 2 semanas'].copy()

margem_total_10_dias = 0
escolhas_diarias = []
todas_combinacoes_validas = []

# Loop para cada dia de produção
for dia in range(dias_de_producao):
    combinacoes_validas = []

    # Gerar todas as combinações possíveis dos produtos
    for i in range(1, len(dados_produto) + 1):
        for comb in combinations_with_replacement(dados_produto.index, i):
            produtos_combinados = dados_produto.loc[list(comb)]
            tempo_total = produtos_combinados['Tempo de produção por receita'].sum()
            
            if tempo_total <= tempo_maximo_diario:
                unidades_vendaveis = produtos_combinados.apply(lambda x: min(x['Quantidade fabricada por produto'], demanda_restante[x.name]), axis=1)
                margem_total = (produtos_combinados['Margem de Contribuição por unidade'] * unidades_vendaveis).sum()
                if margem_total > 0:
                    combinacoes_validas.append((dia+1, produtos_combinados['Produto'].tolist(), margem_total, tempo_total, unidades_vendaveis.sum()))

    todas_combinacoes_validas.extend(combinacoes_validas)

    # Priorizar combinações que atendem a demanda de vendas e maximizam a margem
    combinacoes_validas.sort(key=lambda x: (x[4], x[2]), reverse=True)

    if combinacoes_validas:
        melhor_combinacao = combinacoes_validas[0]
        escolhas_diarias.append((dia+1, melhor_combinacao[1], melhor_combinacao[2]))
        margem_total_10_dias += melhor_combinacao[2]

        # Atualizar demanda restante
        for produto in melhor_combinacao[1]:
            indice_produto = dados_produto[dados_produto['Produto'] == produto].index[0]
            demanda_restante[indice_produto] -= dados_produto.loc[indice_produto, 'Quantidade fabricada por produto']

# Convertendo as combinações e escolhas em DataFrames para exportação
df_combinacoes_validas = pd.DataFrame(todas_combinacoes_validas, columns=['Dia', 'Produtos', 'Margem Total', 'Tempo Total', 'Unidades Vendáveis'])
df_escolhas_diarias = pd.DataFrame(escolhas_diarias, columns=['Dia', 'Produtos Escolhidos', 'Margem Total Dia'])

# Exportar para Excel ou CSV
df_combinacoes_validas.to_excel('./misto/combinacoes_validas_misto.xlsx', index=False)
df_escolhas_diarias.to_excel('./misto/escolhas_diarias_misto.xlsx', index=False)

# Comparação das vendas em 2 semanas versus produção realizada
vendas_vs_producao = dados_produto[['Produto', 'Vendas para 2 semanas']].copy()
vendas_vs_producao['Produzido'] = vendas_vs_producao['Vendas para 2 semanas'] - demanda_restante
vendas_vs_producao['Diferença'] = vendas_vs_producao['Produzido'] - vendas_vs_producao['Vendas para 2 semanas']

vendas_vs_producao.to_excel('./misto/comparacao_vendas_producao_misto.xlsx', index=False)

print(f'Margem total para 10 dias: R$ {margem_total_10_dias:.2f}')


# Plotagem de Gráficos
# 1. Gráfico de linhas das margens diárias
dias = [escolha[0] for escolha in escolhas_diarias]
margens_diarias = [escolha[2] for escolha in escolhas_diarias]
plt.figure(figsize=(10, 6))
plt.plot(dias, margens_diarias, marker='o', linestyle='-')
plt.title('Margem de Contribuição Diária')
plt.xlabel('Dia')
plt.ylabel('Margem de Contribuição')
plt.grid(True)
plt.savefig('./misto/margem_contribuicao_diaria_misto.png')

# 2. Gráfico de comparação entre vendas e produção
plt.figure(figsize=(10, 6))
produtos = vendas_vs_producao['Produto']
vendas = vendas_vs_producao['Vendas para 2 semanas']
produzido = vendas_vs_producao['Produzido']
diferenca = vendas_vs_producao['Diferença']

plt.barh(produtos, vendas, color='lightblue', label='Vendas')
plt.barh(produtos, produzido, color='orange', label='Produzido')
plt.xlabel('Quantidade')
plt.title('Comparação de Vendas e Produção')
plt.legend()
plt.savefig('./misto/comparacao_vendas_producao_misto.png')

# 3. Gráficos para cada dia mostrando combinações válidas
for dia in range(1, dias_de_producao + 1):
    combinacoes_dia = [comb for comb in todas_combinacoes_validas if comb[0] == dia]
    margens = [comb[2] for comb in combinacoes_dia]
    
    # Corrigir o cálculo de quantidades
    quantidades = []
    for comb in combinacoes_dia:
        total_quantidade = 0
        for produto in comb[1]:  # comb[1] é a lista de produtos
            total_quantidade += dados_produto.loc[dados_produto['Produto'] == produto, 'Quantidade fabricada por produto'].sum()
        quantidades.append(total_quantidade)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(quantidades, margens, color='green')
    plt.title(f'Combinações Válidas Dia {dia}')
    plt.xlabel('Quantidade Produzida')
    plt.ylabel('Margem de Contribuição')
    plt.grid(True)
    plt.savefig(f'./misto/combinacoes_validas_dia_{dia}_misto.png')