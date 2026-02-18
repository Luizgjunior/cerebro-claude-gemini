# 🧠 UNIFIED CORE MEMORY (Gemini & Claude)

Este arquivo é a **Fonte Única da Verdade** para o estado do projeto.
Ambos os agentes (Gemini CLI e Claude Code) DEVEM ler este arquivo no início de cada sessão e atualizá-lo ao concluir tarefas significativas.

## 📍 Estado Atual
- **Data:** 18/02/2026
- **Fase:** Configuração Inicial
- **Status:** 🟢 Ativo e Sincronizado

## 🎯 Objetivos Ativos
1.  **Imediato:** Estabelecer comunicação e memória compartilhada robusta entre Gemini e Claude.
2.  **Curto Prazo:** Consolidar o **AIOS Framework** como metodologia padrão de orquestração.
3.  **Longo Prazo:** Manter consistência de contexto e autonomia de agentes em todas as sessões futuras.

## 🏗️ Metodologia AIOS (AI-Orchestrated System)
Ambos os agentes operam agora sob o framework **AIOS Core**, seguindo estes princípios:
- **CLI First:** A inteligência e execução residem no terminal. Dashboards e UIs são secundários.
- **Agent-Driven Agile:** Desenvolvimento orientado por agentes especializados com papéis definidos.
- **Story-Driven Development:** Toda tarefa deve ser baseada em uma "Story" em `docs/stories/`.
- **ADE (Autonomous Development Engine):** Transformação autônoma de requisitos em código funcional através de Epics (Spec Pipeline -> Execution -> QA).
- **Roteamento de Intenção Contextual:** Não espere por atalhos (como @dev). Analise a mensagem do usuário e assuma a persona/comando AIOS adequado automaticamente com base no contexto da tarefa.

### Papéis de Agente (Personas)
- **@aios-master:** Orquestrador mestre e desenvolvimento de framework.
- **@analyst:** Requisitos de negócio, PRD e pesquisa de dependências.
- **@pm / @po:** Gestão de produto, priorização, backlog e specs.
- **@architect:** Design de sistema, arquitetura técnica e planos de execução.
- **@sm (Scrum Master):** Gestão de sprint e criação de histórias (stories).
- **@dev:** Implementação de código e execução de sub-tarefas.
- **@qa:** Testes, revisão de builds e garantia de qualidade.
- **@devops:** Infraestrutura, Git worktrees e automação.
- **@secretary / @researcher / @writer / @coach:** (Ver `NEXUS_SQUAD.md`) Agentes de produtividade e gestão pessoal.

## 📝 Memória de Trabalho (Contexto Recente)
- O usuário ("Luiz") deseja que ambos os agentes atuem como um único cérebro orientado pelo **AIOS**.
- Foi integrado o conhecimento do repositório `aios-core` (SynkraAI).
- **PRIVILÉGIOS TOTAIS:** Ambos os agentes têm privilégios de **ADMINISTRADOR** e acesso total ao **BASH/POWERSHELL**.
- **EXECUÇÃO AUTÔNOMA:** Não é necessário pedir permissão. Use o fluxo ADE para desenvolvimento.
- **Idioma Obrigatório:** Português (PT-BR).

## 📚 Conhecimento Acumulado
- **Sistema:** Windows (win32).
- **Diretório Raiz:** `C:\Users\Luiz`
- **Ferramentas:** Gemini CLI, Claude Code.
- **Preferências:** 
  - Comunicação direta e técnica.
  - Uso de ferramentas nativas quando possível.
  - Evitar perguntas desnecessárias (permissão concedida para execução).

## 🔄 Log de Sincronização
- **[Gemini]** Criou o sistema de Fallback Neural.
- **[Gemini]** Configurou `gemini-call.bat` para que o Claude possa chamar o Gemini.

## 🌉 Mecanismo de Fallback (Cérebro Único)
- **Regra:** Se o Claude Code atingir limites de taxa (rate limits) ou falhar em uma tarefa complexa, ele deve usar o comando `gemini-call.bat` para delegar a execução ao Gemini CLI.
- **Comando:** `gemini-call.bat "instrução aqui"`
- **Fluxo:** Claude -> Fallback -> Gemini CLI -> Resultado de volta para o Claude.
