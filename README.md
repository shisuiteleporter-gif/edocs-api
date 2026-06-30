# E-Docs API - Cliente Python

Cliente Python para integrar com a API pública do E-Docs, o sistema de gestão de documentos e processos administrativos do Governo do Espírito Santo.

## Documentação Oficial

- **API Pública**: https://docs.e-docs.es.gov.br/api/
- **Swagger (Treinamento)**: https://api.treinamento.e-docs.es.gov.br/swagger/
- **Swagger (Produção)**: https://api.e-docs.es.gov.br/swagger/
- **Acesso Cidadão**: https://acessocidadao.es.gov.br

## Instalação

```bash
# Clone ou copie os arquivos
cd edocs-api

# Instale as dependencias
pip install -r requirements.txt

# Configure as credenciais (copie e edite)
cp .env.example .env
# Edite o .env com suas credenciais
```

## Configuração

### 1. Solicitar Acesso à API

Antes de usar, seu sistema precisa estar cadastrado no **Acesso Cidadão** com as permissões aprovadas. Siga os passos em:
https://docs.e-docs.es.gov.br/api/SolicitarAcesso

### 2. Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `EDOCS_CLIENT_ID` | Client ID do seu app no Acesso Cidadão | obrigatório |
| `EDOCS_CLIENT_SECRET` | Client Secret do seu app | obrigatório |
| `EDOCS_AMBIENTE` | `treinamento` ou `producao` | `treinamento` |
| `EDOCS_SCOPE` | Escopos separados por espaço | `api-sigades-consultar` |

### 3. Escopos Disponíveis

| Escopo | Uso | Endpoints |
|--------|-----|-----------|
| `api-sigades-consultar` | Consultas (leitura) | GET em geral |
| `api-sigades-documento` | Upload e captura de documentos | POST /v2/documentos/... |
| `api-sigades-encaminhamento` | Encaminhamentos | POST /v2/encaminhamento/... |
| `api-sigades-processo` | Atos processuais | POST /v2/processos/... |

## Uso Básico

### Consultar Estrutura Organizacional

```python
from edocs_api import EDocsClient, EDocsConfig

# Carregar config de variaveis de ambiente
config = EDocsConfig.from_env()
client = EDocsClient(config)

# Listar patriarcas
patriarcas = client.agente.listar_patriarcas()
for p in patriarcas:
    print(f"{p['id']} - {p['nome']}")

# Listar orgaos
orgaos = client.agente.listar_organizacoes(patriarcas[0]['id'])

# Listar setores
setores = client.agente.listar_setores(orgaos[0]['id'])
```

### Upload e Captura de Documento

```python
# Upload do arquivo
id_arquivo = client.documentos.upload_arquivo("meu-documento.pdf")

# Capturar com assinatura do servidor
resultado = client.documentos.enviar_como_servidor(
    id_arquivo=id_arquivo,
    id_papel="uuid-do-papel",
    id_classe_documental="uuid-da-classe",
    resumo="Memorando de solicitacao",
)
id_evento = resultado["idEvento"]

# Aguardar processamento
evento = client.aguardar_evento(id_evento)
print(f"Documento capturado: {evento['idDocumento']}")
```

### Autuar Processo

```python
id_evento = client.processos.autuar(
    id_papel_autuador="uuid-do-papel",
    id_classe_documental="uuid-da-classe",
    resumo="Solicitacao de aquisicao de equipamentos",
    interessados=[{"tipo": "Papel", "idPapel": "uuid"}],
)
```

### Criar Encaminhamento

```python
id_evento = client.encaminhamentos.novo(
    id_papel_remetente="uuid-do-papel",
    destinatarios=[{"tipo": "Unidade", "id": "uuid-do-setor"}],
    assunto="Analise de documento",
    mensagem="Encaminho para verificacao.",
)
```

## Estrutura do Projeto

```
edocs-api/
├── edocs_api/
│   ├── __init__.py          # Exportacoes principais
│   ├── client.py            # Cliente HTTP com autenticacao OAuth 2.0
│   ├── config.py            # Configuracao (credenciais, ambiente)
│   ├── exceptions.py        # Excecoes personalizadas
│   └── modules/
│       ├── agente.py        # Consultas de estrutura organizacional
│       ├── classificacao.py # Planos e classes de classificacao
│       ├── consultas.py     # Consultas de apoio (eventos, caixas, etc.)
│       ├── documentos.py    # Upload, assinatura e captura
│       ├── encaminhamentos.py # Novo, responder, reencaminhar
│       └── processos.py     # Autuar, despachar, entranhar, etc.
├── examples/
│   ├── 01_consulta_agentes.py
│   ├── 02_upload_documento.py
│   ├── 03_criar_processo.py
│   └── 04_encaminhamento.py
├── .env.example
├── requirements.txt
└── README.md
```

## Fluxo de Operações Assíncronas

Muitas operações de escrita (captura, autuação, encaminhamento) são **assíncronas**:

1. O endpoint retorna `202 Accepted` com um `idEvento`
2. Consulte `GET /v2/eventos/{idEvento}` para ver o status
3. Quando `status = "Executado"`, o recurso foi criado

Use `client.aguardar_evento(id_evento)` para fazer polling automático.

## Boas Práticas

- **Token**: O cliente renova automaticamente o token quando expira
- **Tratamento de erros**: Use `try/except` com as exceções `EDocsAuthError`, `EDocsValidationError`, etc.
- **Ambiente**: Sempre teste no ambiente de **treinamento** primeiro
- **Escopos mínimos**: Solicite apenas os escopos necessários para cada operação

## Licença

Este é um projeto de código aberto para integração com a API pública do E-Docs.
