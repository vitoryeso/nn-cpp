#!/usr/bin/env python3
"""
Aplicação CLI simples para conversar com LLM usando vLLM API
"""

import requests
import sys
import argparse
import json
from typing import List, Dict, Iterator
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

class LLMChat:
    def __init__(self, base_url: str = "http://localhost:9998"):
        self.base_url = base_url.rstrip('/')
        self.chat_url = f"{self.base_url}/v1/chat/completions"
        self.messages: List[Dict[str, str]] = []
        self.console = Console()
        
    def check_server_health(self) -> bool:
        """Verifica se o servidor vLLM está rodando"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> List[str]:
        """Obtém lista de modelos disponíveis"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            return []
        except requests.exceptions.RequestException:
            return []
    
    def send_message_stream(self, message: str, model: str = None, temperature: float = 0.7) -> Iterator[str]:
        """Envia mensagem para o LLM e retorna resposta em streaming"""
        # Adiciona mensagem do usuário ao histórico
        self.messages.append({"role": "user", "content": message})
        
        # Prepara payload para a API
        payload = {
            "model": model or "default",
            "messages": self.messages,
            "temperature": temperature,
            "max_tokens": 1000,
            "stream": True
        }
        
        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                assistant_message = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]  # Remove 'data: '
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        assistant_message += content
                                        yield content
                            except json.JSONDecodeError as e:
                                # Log do erro para debug, mas continua processando
                                self.console.print(f"[dim]Aviso: Erro ao decodificar JSON: {e}[/dim]")
                                continue
                
                # Adiciona resposta completa do assistente ao histórico
                if assistant_message:
                    self.messages.append({"role": "assistant", "content": assistant_message})
            else:
                yield f"Erro HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            yield "Erro: Timeout na requisição"
        except requests.exceptions.RequestException as e:
            yield f"Erro de conexão: {str(e)}"
    
    def send_message(self, message: str, model: str = None, temperature: float = 0.7) -> str:
        """Envia mensagem para o LLM e retorna a resposta (modo não-streaming)"""
        # Adiciona mensagem do usuário ao histórico
        self.messages.append({"role": "user", "content": message})
        
        # Prepara payload para a API
        payload = {
            "model": model or "default",
            "messages": self.messages,
            "temperature": temperature,
            "max_tokens": 1000,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    assistant_message = data['choices'][0]['message']['content']
                    # Adiciona resposta do assistente ao histórico
                    self.messages.append({"role": "assistant", "content": assistant_message})
                    return assistant_message
                else:
                    return "Erro: Resposta inválida do servidor"
            else:
                return f"Erro HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return "Erro: Timeout na requisição"
        except requests.exceptions.RequestException as e:
            return f"Erro de conexão: {str(e)}"
    
    def clear_history(self):
        """Limpa o histórico de conversa"""
        self.messages = []
    
    def show_history(self):
        """Mostra o histórico de conversa com renderização markdown"""
        if not self.messages:
            self.console.print("Nenhuma mensagem no histórico.", style="dim")
            return
        
        for i, msg in enumerate(self.messages, 1):
            role = "Usuário" if msg["role"] == "user" else "Assistente"
            role_color = "blue" if msg["role"] == "user" else "green"
            
            # Cria painel para cada mensagem
            panel_title = f"[{role_color}][{i}] {role}[/{role_color}]"
            if msg["role"] == "assistant":
                # Renderiza markdown para mensagens do assistente
                markdown_content = Markdown(msg['content'])
                panel = Panel(markdown_content, title=panel_title)
            else:
                # Texto simples para mensagens do usuário
                text_content = Text(msg['content'])
                panel = Panel(text_content, title=panel_title)
            
            self.console.print(panel)
            self.console.print()  # Linha em branco entre mensagens
    
    def select_model(self) -> str:
        """Permite ao usuário selecionar um modelo interativamente"""
        models = self.get_available_models()
        if not models:
            self.console.print("❌ Nenhum modelo disponível. Usando modelo padrão.", style="red")
            return "default"
        
        self.console.print("\n📋 Modelos disponíveis:", style="bold blue")
        for i, model in enumerate(models, 1):
            self.console.print(f"  [{i}] {model}", style="cyan")
        
        while True:
            try:
                choice = self.console.input(f"\nEscolha um modelo (1-{len(models)}) ou pressione Enter para usar o padrão: ").strip()
                
                if not choice:
                    return "default"
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(models):
                    selected_model = models[choice_num - 1]
                    self.console.print(f"✅ Modelo selecionado: {selected_model}", style="green bold")
                    return selected_model
                else:
                    self.console.print(f"❌ Por favor, escolha um número entre 1 e {len(models)}", style="red")
            except ValueError:
                self.console.print("❌ Por favor, digite um número válido", style="red")
            except KeyboardInterrupt:
                self.console.print("\n❌ Seleção cancelada. Usando modelo padrão.", style="yellow")
                return "default"

def main():
    parser = argparse.ArgumentParser(description="CLI para conversar com LLM via vLLM API")
    parser.add_argument("--url", default="http://localhost:9998", 
                       help="URL base do servidor vLLM (padrão: http://localhost:9998)")
    parser.add_argument("--model", help="Modelo específico para usar")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Temperatura para geração (padrão: 0.7)")
    parser.add_argument("--no-stream", action="store_true",
                       help="Desabilitar modo streaming")
    
    args = parser.parse_args()
    
    # Cria instância do chat
    chat = LLMChat(args.url)
    
    # Título principal
    title_panel = Panel(
        "[bold blue]🤖 CLI para conversar com LLM[/bold blue]\n[dim]Interface rica com streaming e markdown[/dim]",
        style="blue",
        padding=(1, 2)
    )
    chat.console.print(title_panel)
    
    # Verifica se o servidor está rodando
    chat.console.print("Verificando conexão com o servidor...", style="yellow")
    if not chat.check_server_health():
        error_panel = Panel(
            f"❌ Erro: Não foi possível conectar ao servidor em {args.url}\n"
            "Certifique-se de que o servidor vLLM está rodando.",
            title="Erro de Conexão",
            style="red"
        )
        chat.console.print(error_panel)
        sys.exit(1)
    
    chat.console.print("✅ Servidor conectado com sucesso!", style="green bold")
    
    # Seleciona modelo inicial
    current_model = args.model if args.model else chat.select_model()
    
    # Comandos especiais
    commands_panel = Panel(
        "[bold]💡 Comandos especiais:[/bold]\n"
        "  /clear - Limpar histórico de conversa\n"
        "  /history - Mostrar histórico de conversa\n"
        "  /model - Selecionar/alterar modelo\n"
        "  /stream - Alternar modo streaming\n"
        "  /help - Mostrar esta lista de comandos\n"
        "  /quit ou /exit - Sair do programa",
        title="Comandos",
        style="cyan"
    )
    chat.console.print(commands_panel)
    
    # Status do modelo
    model_status = Panel(
        f"🤖 Modelo atual: [bold green]{current_model}[/bold green]\n"
        f"🌊 Streaming: [bold {'green' if not args.no_stream else 'red'}]{'Ativado' if not args.no_stream else 'Desativado'}[/bold {'green' if not args.no_stream else 'red'}]",
        style="blue"
    )
    chat.console.print(model_status)
    
    # Variável para controlar streaming
    streaming_enabled = not args.no_stream
    
    # Loop principal de conversa
    try:
        while True:
            try:
                user_input = chat.console.input("\n[bold blue]👤 Você:[/bold blue] ").strip()
                
                if not user_input:
                    chat.console.print("💡 Digite uma mensagem ou use um comando (digite /help para ver comandos disponíveis)", style="dim")
                    continue
                
                # Comandos especiais
                if user_input.lower() in ['/quit', '/exit', '/sair']:
                    chat.console.print("👋 Até logo!", style="green bold")
                    break
                elif user_input.lower() == '/clear':
                    chat.clear_history()
                    chat.console.print("🧹 Histórico limpo!", style="green")
                    continue
                elif user_input.lower() == '/history':
                    chat.show_history()
                    continue
                elif user_input.lower() == '/model':
                    new_model = chat.select_model()
                    if new_model and new_model != current_model:
                        current_model = new_model
                        chat.console.print(f"✅ Modelo alterado para: {current_model}", style="green bold")
                    elif new_model == current_model:
                        chat.console.print(f"ℹ️ Modelo já está selecionado: {current_model}", style="yellow")
                    continue
                elif user_input.lower() == '/stream':
                    streaming_enabled = not streaming_enabled
                    status = "Ativado" if streaming_enabled else "Desativado"
                    color = "green" if streaming_enabled else "red"
                    chat.console.print(f"🌊 Streaming {status}", style=f"{color} bold")
                    continue
                elif user_input.lower() == '/help':
                    chat.console.print(commands_panel)
                    continue
                
                # Exibe mensagem do usuário
                user_panel = Panel(
                    user_input,
                    title="[blue]👤 Você[/blue]",
                    style="blue"
                )
                chat.console.print(user_panel)
                
                # Envia mensagem para o LLM
                if streaming_enabled:
                    # Modo streaming
                    chat.console.print("\n[bold green]🤖 Assistente:[/bold green]")
                    
                    # Mostra indicador de carregamento
                    with chat.console.status("[bold green]Processando...", spinner="dots"):
                        # Cria um painel para a resposta em streaming
                        response_content = ""
                        response_panel = Panel(
                            response_content,
                            title="[green]🤖 Assistente[/green]",
                            style="green"
                        )
                        
                        # Usa Live para atualizar o painel em tempo real
                        with Live(response_panel, refresh_per_second=20, console=chat.console) as live:
                            for chunk in chat.send_message_stream(user_input, current_model, args.temperature):
                                if chunk.startswith("Erro"):
                                    chat.console.print(f"\n[red]{chunk}[/red]")
                                    break
                                response_content += chunk
                                # Atualiza o painel com o conteúdo acumulado de forma mais eficiente
                                if response_content.strip():
                                    try:
                                        # Só renderiza markdown se o conteúdo parece ser markdown
                                        if any(marker in response_content for marker in ['**', '*', '`', '#', '-', '1.']):
                                            updated_panel = Panel(
                                                Markdown(response_content),
                                                title="[green]🤖 Assistente[/green]",
                                                style="green"
                                            )
                                        else:
                                            updated_panel = Panel(
                                                Text(response_content),
                                                title="[green]🤖 Assistente[/green]",
                                                style="green"
                                            )
                                    except (ValueError, TypeError):
                                        # Fallback para texto simples se markdown falhar
                                        updated_panel = Panel(
                                            Text(response_content),
                                            title="[green]🤖 Assistente[/green]",
                                            style="green"
                                        )
                                    live.update(updated_panel)
                else:
                    # Modo não-streaming
                    chat.console.print("\n[bold green]🤖 Assistente:[/bold green]")
                    
                    # Mostra indicador de carregamento
                    with chat.console.status("[bold green]Processando...", spinner="dots"):
                        response = chat.send_message(user_input, current_model, args.temperature)
                    
                    if response.startswith("Erro"):
                        chat.console.print(f"[red]{response}[/red]")
                    else:
                        # Renderiza markdown
                        response_panel = Panel(
                            Markdown(response),
                            title="[green]🤖 Assistente[/green]",
                            style="green"
                        )
                        chat.console.print(response_panel)
                
            except (KeyboardInterrupt, EOFError):
                chat.console.print("\n👋 Até logo!", style="green bold")
                break
                
    except (KeyboardInterrupt, EOFError):
        chat.console.print("\n👋 Até logo!", style="green bold")
    except Exception as e:
        error_panel = Panel(
            f"❌ Erro inesperado: {str(e)}",
            title="Erro",
            style="red"
        )
        chat.console.print(error_panel)
        sys.exit(1)

if __name__ == "__main__":
    main()
