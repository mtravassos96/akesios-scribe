# Roadmap — Assistente de Laudo Clínico (áudio → rascunho, 100% offline)

> Planejamento do meu **primeiro projeto de ponta a ponta feito sozinho**.
> Este arquivo é só o **mapa**. O **código é meu** — ver a Regra abaixo.

## Regra deste projeto (minha, não do Claude)

Escrevo **todo o código com a minha própria cabeça**, sem IA gerando por mim — no
máximo autocomplete do editor, e mesmo esse eu tento evitar. Uso Claude/Claude Code
todo dia no trabalho, mas quero poder dizer, com verdade, que **este projeto eu fiz
sozinho**. Então:
- Este roadmap diz **o quê** e **o que estudar** — nunca o **como** (nada de código, nem trechos, nem pseudocódigo que entregue a solução).
- Quando eu travar, eu leio a **documentação oficial** e bato cabeça antes de pedir ajuda.
- Se eu pedir ajuda a alguém (ou à IA), registro isso no `LEARNINGS.md` — honestidade comigo mesmo.

## O problema (por que este projeto existe)

Um médico grava o áudio da consulta no celular. Digitar o laudo depois é lento e
tira tempo do paciente. Este projeto recebe o áudio e devolve um **rascunho de laudo**
para o médico **revisar e assinar**.

**O diferencial é ser offline.** Transcrição e LLM rodam **na própria máquina**
(Faster-Whisper + Ollama) → **o áudio do paciente nunca sai do computador**. Isso é
privacidade/LGPD de verdade, não enfeite — e é a primeira frase do README no final.
**Humano no circuito:** é sempre um *rascunho*; quem decide e assina é o médico.

## Princípios

1. **Incremental.** Cada milestone é uma coisa que **roda sozinha**. Só avanço quando o anterior funciona.
2. **Offline-first.** Nada de API paga; tudo local e gratuito.
3. **Rascunho, não decisão.** O sistema assiste; não substitui o médico.
4. **Commit a cada milestone que funciona.** O histórico conta a evolução.
5. **Nunca commitar dado real de paciente.** Testo com áudio **fake/sintético**. Áudios e saídas entram no `.gitignore`.

## Stack (já decidida por mim)

| Camada | Ferramenta |
|---|---|
| Ingestão | pasta vigiada (**watchdog**) → depois e-mail (**IMAP**) |
| Conversão de áudio | **FFmpeg** |
| Transcrição | **Faster-Whisper** |
| LLM (rascunho) | **Ollama** (Llama 3 / Gemma / Mistral) |
| Validação da saída | **Pydantic** |
| Empacotar (fim) | **pytest**, **Docker** |

---

## Milestones

> Para cada um: **Objetivo** · **Pronto quando** (resultado observável) · **O que estudar** (tópicos + docs, sem código) · **Armadilhas a antecipar**.

### M0 — Ambiente
- **Objetivo:** máquina pronta pra desenvolver.
- **Pronto quando:** consigo rodar um "hello world" em Python num venv; FFmpeg responde no terminal; Ollama roda e eu baixei um modelo; Faster-Whisper instalado.
- **Estudar:** ambientes virtuais em Python (venv); como instalar e testar FFmpeg no Windows; como o Ollama baixa e serve um modelo local. Docs: python.org (venv), ffmpeg.org, ollama.com/docs.
- **Armadilhas:** FFmpeg precisa estar no PATH; o primeiro `pull` de modelo é grande (GB).

### M1 — Detectar arquivo novo numa pasta
- **Objetivo:** um programa que "escuta" a pasta `audios/` e reage quando um arquivo aparece.
- **Pronto quando:** eu solto um arquivo qualquer em `audios/` e o programa imprime o nome dele; o programa fica rodando (não encerra sozinho).
- **Estudar:** como a biblioteca **watchdog** avisa sobre eventos do sistema de arquivos (ler o quickstart oficial). Perguntas-guia: como recebo um aviso quando um arquivo é *criado*? como um programa fica "vivo" esperando eventos em vez de terminar? Docs: watchdog (readthedocs/pypi).
- **Armadilhas:** o evento "criado" pode disparar **antes de o arquivo terminar de copiar** (resolvo isso no M2).

### M2 — Esperar o arquivo estar pronto
- **Objetivo:** só processar quando o arquivo terminou de ser gravado.
- **Pronto quando:** copio um arquivo grande e o programa só reage **depois** que ele está completo (imprime nome + tamanho final).
- **Estudar:** como saber que um arquivo parou de crescer (ideia: observar o tamanho ao longo do tempo); como ler propriedades de arquivo em Python. Perguntas-guia: como comparo o tamanho agora vs. daqui a um instante?
- **Armadilhas:** formatos de áudio de celular (`.m4a`, `.ogg`, `.opus`) — anotar quais aparecem.

### M3 — Transcrever o áudio
- **Objetivo:** áudio → `transcricao.txt`.
- **Pronto quando:** dou um áudio de teste e sai um `.txt` com a transcrição legível.
- **Estudar:** como o **Faster-Whisper** recebe um arquivo e devolve texto; papel do **FFmpeg** na conversão de formato; tamanhos de modelo (tiny→large) e o trade-off velocidade × qualidade; como forçar o idioma (pt). Docs: repositório do Faster-Whisper.
- **Armadilhas:** áudio longo demora; escolher um modelo que caiba na minha máquina; áudio de celular pode precisar de conversão antes.

### M4 — Gerar o rascunho de laudo com a LLM
- **Objetivo:** `transcricao.txt` → `laudo.txt`.
- **Pronto quando:** a transcrição vira um rascunho de laudo coerente em `laudo.txt`.
- **Estudar:** como chamar o **Ollama** localmente e mandar um prompt; o que é um **system prompt** vs. o texto do usuário; por que **temperatura baixa** dá saída mais consistente; como escrever um prompt que peça as seções do laudo. Docs: ollama.com/docs (API local).
- **Armadilhas:** a LLM "inventa" (alucina) — por isso é rascunho + revisão humana; definir o que fazer quando a transcrição está ruim.

### M5 — Ciclo de vida dos arquivos
- **Objetivo:** organizar entrada, sucesso e falha.
- **Pronto quando:** áudio processado vai pra `Processados/`; se algo quebra, vai pra `Falhas/` e o programa não morre.
- **Estudar:** mover/renomear arquivos em Python; tratar exceções (try/except) sem derrubar o processo. Perguntas-guia: o que acontece hoje se a transcrição falha no meio?
- **Armadilhas:** não sobrescrever um arquivo de mesmo nome; não reprocessar o que já foi feito.

### M6 — Robustez
- **Objetivo:** deixar confiável para rodar sozinho.
- **Pronto quando:** tem **log** do que aconteceu (quando, qual arquivo, sucesso/falha); os caminhos e o modelo vêm de um **arquivo de config**, não fixos no código; nada é reprocessado.
- **Estudar:** logging em Python; ler config de um arquivo (`.env`/`.ini`/`.yaml`); como marcar algo como "já processado". 
- **Armadilhas:** segredos (senha de e-mail, no M8) **nunca** no código nem no Git.

### M7 — Saída estruturada (o upgrade que vale ouro)
- **Objetivo:** a LLM devolve o laudo como **dados estruturados (JSON)**, validados, e eu renderizo pra `.md`/`.txt`.
- **Pronto quando:** peço um JSON com campos definidos (ex.: queixa, história, hipótese, conduta); valido com **Pydantic**; se vier inválido, eu **tento de novo**; só então gero o documento final.
- **Estudar:** por que um contrato de saída (schema) é mais confiável que texto solto; como o Pydantic valida dados; como pedir JSON pra uma LLM e o que fazer quando ela foge do formato. Docs: pydantic.dev.
- **Por que importa:** este é **o tema central de entrevista de IA** ("reliable structured outputs"). Este milestone é a prova pública de que eu sei fazer.

### M8 — Ingestão por e-mail (fecha a etapa "celular → email")
- **Objetivo:** o áudio chega por e-mail e cai em `audios/` sozinho.
- **Pronto quando:** mando um áudio anexo pra uma caixa de e-mail e ele aparece em `audios/` sem eu tocar.
- **Estudar:** como ler e-mails e baixar anexos por **IMAP** em Python; como guardar a senha com segurança (senha de app, variável de ambiente). Docs: `imaplib` (docs do Python).
- **Armadilhas:** provedores exigem "senha de app"; não baixar o mesmo e-mail duas vezes.

### M9 — Virar portfólio
- **Objetivo:** um repo que um recrutador entende em 30 segundos.
- **Pronto quando:** tem **README** com **Problema → Solução → Diagrama → Como rodar → Resultado**; um **áudio de exemplo sintético** (nunca de paciente real); um **GIF/vídeo de ~60s**; alguns **testes (pytest)**; licença; e, se der, `docker-compose`.
- **Estudar:** o que faz um bom README de projeto; testar em Python com pytest; empacotar com Docker (Ollama + o worker).
- **Armadilhas:** ⚠️ **jamais** commitar áudio/laudo real de paciente — `.gitignore` desde o M1.

---

## Definição de "terminado o suficiente para mostrar"

Do M1 ao M7 rodando ponta a ponta, com README + diagrama + um exemplo reproduzível.
M8 e M9 elevam, mas já dá pra apresentar antes deles.

## Ideias de evolução (depois, se quiser)

- Template de laudo por especialidade.
- Exportar PDF assinável.
- Fila para vários áudios ao mesmo tempo.
- Métrica de tempo economizado por consulta.

## LEARNINGS.md (recomendação forte)

Manter, ao lado do código, um `LEARNINGS.md` onde eu escrevo **o que travou e como
resolvi** em cada milestone. Serve pra duas coisas: fixa o aprendizado e vira material
pronto pra contar na entrevista ("bug mais difícil que resolvi sozinho").
