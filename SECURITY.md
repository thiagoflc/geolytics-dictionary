# Security Policy

## Versões suportadas

A última versão publicada em `main` recebe correções de segurança. Versões anteriores não recebem patches.

| Versão          | Suporte |
| --------------- | ------- |
| `main` (HEAD)   | ✅      |
| Tags anteriores | ❌      |

## Reportando uma vulnerabilidade

**Não abra issues públicas no GitHub para vulnerabilidades de segurança.**

Use um dos canais privados:

1. **GitHub Private Vulnerability Reporting** — preferido. Vá em **Security → Advisories → Report a vulnerability** neste repositório.
2. **E-mail**: `thiagoflc@gmail.com` com assunto `[SECURITY] geobrain`.

Inclua:

- Descrição da vulnerabilidade.
- Passos para reproduzir.
- Versão / commit afetado.
- Impacto estimado.
- (Opcional) sugestão de correção.

## Tempo de resposta

- **Reconhecimento**: até 72 horas.
- **Avaliação inicial**: até 7 dias.
- **Patch**: até 30 dias para vulnerabilidades críticas; até 90 para baixa severidade.

## Escopo

Em escopo:

- Código em `python/`, `scripts/`, `mcp/geobrain-mcp/`.
- Workflows de CI em `.github/workflows/`.
- Validadores SHACL e geração de dados.

Fora de escopo:

- Vulnerabilidades em dependências de terceiros — reporte upstream.
- Engenharia social ou ataques físicos.
- Conteúdo dos dados regulatórios públicos (ANP/SIGEP).

## Disclosure

Após o patch, publicaremos um GitHub Security Advisory com créditos ao reporter (a menos que solicitada anonimato).
