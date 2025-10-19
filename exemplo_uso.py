#!/usr/bin/env python3
"""
Exemplo de uso da aplicação CLI para conversar com LLM
"""

from llm_cli import LLMChat

def exemplo_basico():
    """Exemplo básico de uso da classe LLMChat"""
    print("=== Exemplo de Uso da Classe LLMChat ===\n")
    
    # Cria instância do chat
    chat = LLMChat("http://localhost:8000")
    
    # Verifica se o servidor está rodando
    if not chat.check_server_health():
        print("❌ Servidor não está rodando. Inicie o servidor vLLM primeiro.")
        return
    
    print("✅ Servidor conectado!")
    
    # Lista modelos disponíveis
    models = chat.get_available_models()
    if models:
        print(f"📋 Modelos: {', '.join(models)}")
    
    # Exemplo de conversa
    print("\n--- Exemplo de Conversa ---")
    
    # Primeira mensagem
    resposta1 = chat.send_message("Olá! Como você está?")
    print(f"Usuário: Olá! Como você está?")
    print(f"Assistente: {resposta1}\n")
    
    # Segunda mensagem (com contexto)
    resposta2 = chat.send_message("Qual é a capital do Brasil?")
    print(f"Usuário: Qual é a capital do Brasil?")
    print(f"Assistente: {resposta2}\n")
    
    # Mostra histórico
    print("--- Histórico da Conversa ---")
    chat.show_history()
    
    # Limpa histórico
    print("\n--- Limpando Histórico ---")
    chat.clear_history()
    print("Histórico limpo!")

if __name__ == "__main__":
    exemplo_basico()
