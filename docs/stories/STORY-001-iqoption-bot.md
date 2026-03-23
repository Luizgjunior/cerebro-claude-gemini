# Story: Robô de Operações Automáticas IQ Option

**ID:** STORY-001
**Título:** Conexão e Estratégia Inicial do Robô
**Status:** 🟢 Iniciada
**Dificuldade:** Média (Desenvolvimento para Leigo)

## 🎯 Objetivo
Criar um robô em Python que se conecte à IQ Option e execute operações baseadas em uma estratégia simples de análise de velas (candles).

## 📋 Requisitos (O que o robô precisa fazer)
1. **Conectar com segurança:** Entrar na conta do Luiz usando e-mail e senha (armazenados localmente).
2. **Selecionar Conta:** Operar obrigatoriamente na conta de treinamento (DEMO) para segurança inicial.
3. **Analisar o Mercado:** Olhar as últimas velas de um par de moedas (ex: EUR/USD).
4. **Executar Ordem:** Se a estratégia bater, ele faz a compra (CALL) ou venda (PUT).

## 🧪 Critérios de Aceite (Como saberemos que deu certo)
- [ ] O robô consegue fazer o login e mostrar o saldo da conta demo.
- [ ] O robô consegue ler o preço atual do mercado.
- [ ] O robô faz uma operação de teste de R$ 2,00 na conta demo.

---
*Planejado por: @architect (AIOS Core)*
