# Pesquisa de Preços — Compras.gov.br (adaptado por Bruno Manoel)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://6u9u9kh8bgu3hktkpvk723.streamlit.app/)

Aplicação web desenvolvida em **Streamlit** para consulta e exportação de dados de pesquisa de preços do portal [Compras.gov.br](https://www.gov.br/compras).

---

## Sobre

Esta ferramenta acessa a **API de Dados Abertos do Compras.gov.br** e permite que servidores e gestores públicos consultem preços praticados em compras governamentais de materiais e serviços, com exportação em CSV compatível com Excel (pt-BR).

---

## Funcionalidades

- Consulta de preços de **materiais** e **serviços** por código do catálogo CATMAT/CATSER
- Seleção de página e quantidade de itens por página
- Feedback visual com indicador de carregamento durante a requisição
- Exibição dos resultados em **tabela interativa** ordenável e filtrável
- Colunas renomeadas para **português** (ex.: `precoUnitario` → `Preço Unitário (R$)`)
- Exportação em **CSV com separador `;`** e encoding **UTF-8 BOM** — abre corretamente no Excel do Windows sem quebrar acentos
- Valores numéricos formatados com vírgula decimal (padrão pt-BR), reconhecidos como números pelo Excel
- Limpeza automática do estado entre consultas

---

## Pré-requisitos

- Python 3.12+
- Git

---

## Como executar localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/magnumcosta/apps.git
cd apps
```

### 2. Criar e ativar o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
streamlit run streamlit_app.py
```

### 5. Desativar o ambiente virtual (quando terminar)
```bash
deactivate
```

---

## Acesso

### Online (deploy)

Acesse diretamente pelo navegador, sem necessidade de instalação:

**[https://suportedadoslivres.streamlit.app/](https://6u9u9kh8bgu3hktkpvk723.streamlit.app/)**

### Local

Após executar a aplicação, ela abrirá automaticamente em:

```
http://localhost:8501
```

---

## Como usar

1. Acesse o [Catálogo de Compras](https://catalogo.compras.gov.br/cnbs-web/busca) e localize o código do material ou serviço desejado
2. Selecione o **tipo de item** (Material ou Serviço)
3. Informe o **Código do Item de Catálogo**
4. Ajuste a **página** e a quantidade de **itens por página**
5. Clique em **Consultar**
6. Visualize os resultados na tabela interativa
7. Faça o **download em CSV** compatível com Excel

---

## Tecnologias

| Tecnologia | Versão | Função |
|------------|--------|--------|
| Python | 3.12 | Linguagem base |
| Streamlit | 1.55.0 | Framework de interface web |
| Pandas | 2.3.3 | Manipulação e exportação de dados |
| Requests | 2.32.5 | Consumo da API REST |

---

## Fonte de Dados

**API de Dados Abertos do Compras.gov.br**
- Material: `https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial`
- Serviço: `https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/3_consultarServico`

---

