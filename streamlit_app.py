import streamlit as st
import requests
import pandas as pd

CONSULTAR_MATERIAL_URL = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial'
CONSULTAR_SERVICO_URL  = 'https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico'

REQUEST_TIMEOUT = 30  # segundos


def formatar_preco_reais(valor):
    """Formata um float como preço no padrão brasileiro (ex: 1.234,56)."""
    if valor is None:
        return 'Preço não disponível'
    return f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def float_para_csv(valor):
    """Converte float para string decimal BR (vírgula, sem ponto de milhar).
    Mantém o valor reconhecível como número pelo Excel pt-BR."""
    if isinstance(valor, float):
        return f'{valor:.2f}'.replace('.', ',')
    return valor


# Mapeamento de nomes de colunas da API → rótulos legíveis em português
RENOMEAR_COLUNAS = {
    'idCompra':                    'ID Compra',
    'idItemCompra':                'ID Item',
    'forma':                       'Forma',
    'modalidade':                  'Modalidade',
    'criterioJulgamento':          'Critério Julgamento',
    'numeroItemCompra':            'Nº Item',
    'descricaoItem':               'Descrição do Item',
    'codigoItemCatalogo':          'Cód. Catálogo',
    'nomeUnidadeMedida':           'Unidade Medida',
    'siglaUnidadeMedida':          'Sigla Unidade Medida',
    'nomeUnidadeFornecimento':     'Unidade Fornecimento',
    'siglaUnidadeFornecimento':    'Sigla Unid. Fornecimento',
    'capacidadeUnidadeFornecimento': 'Capacidade Unid. Fornecimento',
    'quantidade':                  'Quantidade',
    'precoUnitario':               'Preço Unitário (R$)',
    'percentualMaiorDesconto':     'Desconto (%)',
    'niFornecedor':                'CNPJ/CPF Fornecedor',
    'nomeFornecedor':              'Fornecedor',
    'marca':                       'Marca',
    'codigoUasg':                  'Cód. UASG',
    'nomeUasg':                    'UASG',
    'codigoMunicipio':             'Cód. Município',
    'municipio':                   'Município',
    'estado':                      'UF',
    'codigoOrgao':                 'Cód. Órgão',
    'nomeOrgao':                   'Órgão',
    'poder':                       'Poder',
    'esfera':                      'Esfera',
    'dataCompra':                  'Data da Compra',
    'dataHoraAtualizacaoCompra':   'Atualização Compra',
    'dataHoraAtualizacaoItem':     'Atualização Item',
    'dataResultado':               'Data Resultado',
    'dataHoraAtualizacaoUasg':     'Atualização UASG',
    'codigoClasse':                'Cód. Classe',
    'nomeClasse':                  'Classe',
    'objetoCompra':                'Objeto da Compra',
    'descricaoDetalhadaItem':      'Descrição Detalhada',
}

# Colunas que SEMPRE devem aparecer (não podem ser removidas)
COLUNAS_OBRIGATORIAS = [
    'ID Compra',
    'ID Item',
    'Nº Item',
    'Descrição do Item',
    'Cód. Catálogo',
    'CNPJ/CPF Fornecedor',
    'Fornecedor',
    'Data da Compra'
]

def obter_itens(tipo_item, codigo_item_catalogo, pagina, tamanho_pagina, data_inicio=None, data_fim=None):
    """Consulta a API do Compras.gov.br com filtro de data opcional."""
    url = CONSULTAR_MATERIAL_URL if tipo_item == 'Material' else CONSULTAR_SERVICO_URL
    
    # ATUALIZAÇÃO AQUI: A API mudou os parâmetros esperados
    params = {
        'pagina': pagina,
        'tamanhoPagina': tamanho_pagina,
        'tipo': 'codigoItemCatalogo',           # Passa a ser obrigatório avisar o tipo de código
        'codigo': codigo_item_catalogo.strip()  # Passa apenas 'codigo' em vez de 'codigoItemCatalogo'
    }

    # Adiciona filtro de data apenas se o usuário informou
    if data_inicio:
        params['dataCompraInicio'] = data_inicio.strftime('%Y-%m-%d')
    if data_fim:
        params['dataCompraFim'] = data_fim.strftime('%Y-%m-%d')

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        json_response = response.json()
        
        itens = json_response.get('resultado', [])
        paginas_restantes = json_response.get('paginasRestantes', 0)
        total_paginas = json_response.get('totalPaginas', 0)
        
        return itens, paginas_restantes, total_paginas
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro na API: {err.response.status_code} - {err.response.text}")
        return [], 0, 0
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        return [], 0, 0
    
@st.dialog("Selecionar Colunas para Exibição")
def selecionar_colunas_dialog():
    """Modal para o usuário escolher quais colunas quer ver."""
    todas_colunas = list(RENOMEAR_COLUNAS.values())  # todas as colunas traduzidas
    
    # Recupera seleção anterior ou usa todas
    if 'colunas_selecionadas' not in st.session_state:
        st.session_state['colunas_selecionadas'] = todas_colunas.copy()
    
    # Multiselect - desabilita as obrigatórias (mas elas sempre aparecem)
    colunas_escolhidas = st.multiselect(
        "Escolha as colunas que deseja visualizar:",
        options=todas_colunas,
        default=st.session_state['colunas_selecionadas'],
        help="As colunas em negrito são obrigatórias e não podem ser removidas."
    )
    
    # Garante que as obrigatórias sempre estejam presentes
    for obr in COLUNAS_OBRIGATORIAS:
        if obr not in colunas_escolhidas:
            colunas_escolhidas.append(obr)
    
    if st.button("Salvar seleção", type="primary"):
        st.session_state['colunas_selecionadas'] = colunas_escolhidas
        st.rerun()   # fecha o modal e atualiza
    
# =============================================================================
# Interface
# =============================================================================
st.title("Pesquisa de Preços de Materiais e/ou Serviços")
st.markdown(
    "Localize o código do material ou serviço no "
    "[Catálogo de Compras](https://catalogo.compras.gov.br/cnbs-web/busca) "
    "antes de consultar."
)

st.divider()

# ====================== FILTROS ======================
col1, col2, col3 = st.columns([1.5, 1.5, 1.5])

with col1:
    tipo_item = st.selectbox("Tipo de item", ['Material', 'Serviço'], key='tipo_item')
    codigo_item_catalogo = st.text_input("Código do Item de Catálogo", value="", key='codigo_item_catalogo')

with col2:
    data_inicio = st.date_input(
        "Data Inicial",
        value=None,           # None = sem filtro
        format="DD/MM/YYYY"
    )
    data_fim = st.date_input(
        "Data Final",
        value=None,
        format="DD/MM/YYYY"
    )

with col3:
    pagina = st.number_input("Página", min_value=1, value=1, step=1)
    tamanho_pagina = st.number_input("Itens por página", min_value=10, value=50, step=10)

# Botão para configurar colunas
if st.button("⚙️ Configurar colunas visíveis", help="Escolha quais colunas aparecerão na tabela e no CSV"):
    selecionar_colunas_dialog()

if st.button('Consultar', type='primary'):
    # Limpa resultado anterior a cada nova consulta
    st.session_state.pop('itens', None)
    st.session_state.pop('paginas_restantes', None)
    st.session_state.pop('total_paginas', None)

    if not codigo_item_catalogo.strip():
        st.warning("Por favor, informe o código do item de catálogo para realizar a consulta.")
    else:
        with st.spinner('Consultando a API do Compras.gov.br...'):
            itens, paginas_restantes, total_paginas = obter_itens(
                tipo_item, 
                codigo_item_catalogo, 
                pagina, 
                tamanho_pagina,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
        if itens:
            st.session_state['itens'] = itens
            st.session_state['paginas_restantes'] = paginas_restantes
            st.session_state['total_paginas'] = total_paginas
        else:
            st.error("Nenhum item encontrado. Verifique o código informado ou tente novamente.")

# Exibe resultados e botão de download fora do bloco do botão,
# para que persistam entre reruns do Streamlit.
if st.session_state.get('itens'):
    try:
        itens = st.session_state['itens']
        if isinstance(itens, list) and all(isinstance(item, dict) for item in itens):
            df_completo = pd.json_normalize(itens)

            # Renomeia todas as colunas para português
            df_completo = df_completo.rename(columns=RENOMEAR_COLUNAS)

            # Pega as colunas que o usuário escolheu (ou todas na primeira vez)
            if 'colunas_selecionadas' not in st.session_state or not st.session_state['colunas_selecionadas']:
                st.session_state['colunas_selecionadas'] = list(RENOMEAR_COLUNAS.values())

            colunas_para_mostrar = st.session_state['colunas_selecionadas']

            colunas_para_mostrar = [c for c in COLUNAS_OBRIGATORIAS if c in colunas_para_mostrar] + \
                       [c for c in colunas_para_mostrar if c not in COLUNAS_OBRIGATORIAS]

            # Interseção das colunas para evitar erros caso a API não retorne todas
            colunas_existentes = [c for c in colunas_para_mostrar if c in df_completo.columns]

            # DataFrame de exibição (com formatação bonita de preços)
            df_exibicao = df_completo[colunas_existentes].copy()
            df_exibicao = df_exibicao.map(
                lambda x: formatar_preco_reais(x) if isinstance(x, float) else x
            )

            # DataFrame para exportação CSV (mantém números com vírgula)
            df_csv = df_completo[colunas_existentes].copy()
            df_csv = df_csv.map(float_para_csv)

            st.success(
                f"Total de páginas: {st.session_state['total_paginas']} | "
                f"Páginas restantes: {st.session_state['paginas_restantes']}"
            )

            # Mostra a tabela apenas com as colunas selecionadas
            st.dataframe(df_exibicao, use_container_width=True)

            # Download com exatamente as mesmas colunas
            csv = df_csv.to_csv(sep=';', index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Download dos dados em CSV",
                data=csv,
                file_name='pesquisa_precos.csv',
                mime='text/csv',
                type='secondary',
            )

        else:
            st.error("Formato dos itens inválido para normalização.")
    except Exception as e:
        st.error(f"Erro ao processar os itens: {e}")