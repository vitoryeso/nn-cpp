# CLI para Conversar com LLM via vLLM API

Uma aplicação CLI simples em Python para conversar com modelos de linguagem grandes (LLM) através da API vLLM.

## Características

- ✅ Interface de linha de comando interativa
- ✅ Suporte completo à API vLLM
- ✅ Histórico de conversa persistente
- ✅ Verificação de saúde do servidor
- ✅ Listagem de modelos disponíveis
- ✅ Comandos especiais para gerenciar conversa
- ✅ Tratamento robusto de erros

## Pré-requisitos

- Python 3.7+
- Servidor vLLM rodando (ex: `http://localhost:8000`)
- Biblioteca `requests` instalada

## Instalação

1. Clone ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

### Uso Básico

```bash
python llm_cli.py
```

### Uso com Parâmetros

```bash
# Especificar URL do servidor
python llm_cli.py --url http://localhost:8000

# Usar modelo específico
python llm_cli.py --model "gpt-3.5-turbo"

# Ajustar temperatura
python llm_cli.py --temperature 0.9
```

### Comandos Especiais

Durante a conversa, você pode usar:

- `/clear` - Limpar histórico de conversa
- `/history` - Mostrar histórico de conversa
- `/quit` ou `/exit` - Sair do programa

### Exemplo de Uso Programático

```python
from llm_cli import LLMChat

# Criar instância
chat = LLMChat("http://localhost:8000")

# Verificar servidor
if chat.check_server_health():
    # Enviar mensagem
    resposta = chat.send_message("Olá! Como você está?")
    print(resposta)
```

## Estrutura dos Arquivos

- `llm_cli.py` - Aplicação principal
- `exemplo_uso.py` - Exemplo de uso programático
- `requirements.txt` - Dependências Python
- `README.md` - Este arquivo

## API vLLM Suportada

A aplicação usa o endpoint `/v1/chat/completions` da API vLLM, que é compatível com a especificação OpenAI Chat Completions API.

### Endpoints Utilizados

- `GET /health` - Verificação de saúde
- `GET /v1/models` - Listagem de modelos
- `POST /v1/chat/completions` - Geração de respostas

## Solução de Problemas

### Servidor não conecta

```
❌ Erro: Não foi possível conectar ao servidor em http://localhost:8000
```

**Solução:** Certifique-se de que o servidor vLLM está rodando na URL especificada.

### Timeout na requisição

```
Erro: Timeout na requisição
```

**Solução:** O modelo pode estar processando uma resposta longa. Tente novamente ou use um modelo menor.

### Modelo não encontrado

```
⚠️ Aviso: Modelo 'modelo-x' não encontrado. Usando modelo padrão.
```

**Solução:** Verifique os modelos disponíveis com `/models` ou use um modelo válido.

## Desenvolvimento

Para contribuir ou modificar:

1. O código está bem documentado
2. Use type hints para melhor manutenibilidade
3. Teste com diferentes modelos e configurações
4. Mantenha compatibilidade com a API vLLM

## Licença

Este projeto é de código aberto e pode ser usado livremente.
