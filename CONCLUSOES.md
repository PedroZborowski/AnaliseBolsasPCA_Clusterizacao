# Guia de Conclusões — "DNA do Mercado" (PCA + K-Means)

> **Como usar este arquivo:** este documento não substitui rodar o app e olhar os
> números reais — ele é um **roteiro de interpretação**. Como os dados vêm ao vivo do
> Yahoo Finance (últimos ~252 pregões a partir da data em que você abrir o painel), os
> valores exatos de variância explicada, os membros de cada cluster e o `k` ótimo pelo
> silhouette score **vão mudar de execução para execução**. O que dificilmente muda é a
> *lógica econômica* por trás dos agrupamentos, porque ela reflete eventos reais que
> afetaram essas 40 empresas nos últimos ~12 meses. Use as narrativas abaixo como
> hipóteses para checar contra o que o painel realmente mostrar — se baterem, ótimo
> exemplo para a apresentação; se não baterem, isso também é uma conclusão interessante
> (o mercado pode estar precificando outra coisa).

## 1. O universo de dados

40 ações americanas de grande capitalização, divididas em 8 setores "de manual":

| Setor | Tickers |
|---|---|
| Tecnologia | AAPL, MSFT, GOOGL, NVDA, META, ORCL, CRM, ADBE, AMD, INTC |
| Financeiro | JPM, BAC, GS, MS, WFC, AXP, C |
| Saúde | JNJ, PFE, UNH, MRK, ABBV, LLY |
| Energia | XOM, CVX, COP, SLB |
| Consumo | KO, PEP, WMT, PG, MCD, NKE |
| Industrial | BA, CAT, GE, HON |
| Automotivo | TSLA, F |
| Telecom | VZ, T |

A pergunta central do trabalho é: **a classificação "de manual" (GICS/setor) ainda
explica como essas ações se movem no dia a dia, ou o mercado agrupa as empresas por
outra lógica** (sensibilidade a juros, exposição a commodities, exposição à IA, risco
geopolítico, etc.)? PCA + K-Means são exatamente as ferramentas para responder isso:
se os clusters do K-Means baterem com a coluna "Setor", a hipótese de manual se
confirma; se cruzarem setores, há uma força macro mais forte unindo essas empresas.

---

## 2. Interpretando os Componentes Principais (PCA)

O PCA não sabe o que é "setor" — ele só enxerga 252 números (retornos diários) por
ação e procura os eixos de máxima variância comum. Cada componente principal (PC) é,
na prática, um "fator de risco" latente. Padrões típicos observados em ações
americanas nos últimos anos, que você deve procurar nos seus resultados:

### PC1 — "o mercado em geral" (fator beta)
Quase sempre o primeiro componente captura o movimento conjunto do mercado (o que em
finanças se chama de fator de mercado/beta). Ele costuma explicar entre **30% e 45%**
da variância sozinho, porque quando o S&P 500 sobe ou cai, a maioria das 40 ações se
move na mesma direção. **Conclusão pronta:** "PC1 sozinho já mostra que diversificação
setorial não é suficiente para reduzir risco — a maior parte do movimento das 40
ações é explicada por um único fator de mercado comum."

### PC2 — geralmente separa "crescimento/IA" de "defensivo/valor"
Com a fase de forte investimento em infraestrutura de IA (Nvidia, hiperescaladores)
puxando o mercado desde 2023–2024, é comum que PC2 separe:
- de um lado: **NVDA, AMD, MSFT, GOOGL, META, ORCL, CRM, ADBE** (tecnologia ligada a IA
  e nuvem, alta volatilidade, sensíveis a expectativas de crescimento);
- do outro: **KO, PEP, PG, WMT, JNJ, VZ, T** (defensivas, dividendos estáveis, baixa
  beta, mais sensíveis a taxa de juros do que a "hype").

**Conclusão pronta:** "PC2 revela um eixo 'crescimento especulativo vs. defensivo
pagador de dividendo' — o mesmo eixo que analistas chamam de *growth vs. value* — e
não um eixo setorial."

### PC3 — costuma capturar o fator "commodity/energia"
Com a alta volatilidade do petróleo (tensões no Oriente Médio, cortes/decisões da
OPEP+, e efeitos de segunda ordem da guerra na Ucrânia sobre o mercado global de
energia), é comum um componente isolar **XOM, CVX, COP, SLB** como um bloco quase
"sozinho", pouco correlacionado com o resto do mercado.

**Conclusão pronta:** "Energia se comporta como uma classe de ativos quase
independente do resto da carteira — reagindo a choques geopolíticos de oferta de
petróleo/gás, e não ao sentimento geral de bolsa. Isso é consistente com a tensão
geopolítica prolongada (guerra na Ucrânia, conflitos no Oriente Médio) que mantém o
prêmio de risco geopolítico embutido no preço do petróleo desde 2022."

### PC4/PC5 em diante — ruído específico de empresa ou eventos pontuais
A partir do quarto ou quinto componente, a variância explicada cai para poucos pontos
percentuais cada. Aqui é onde aparecem eventos **idiossincráticos** de uma única
empresa (ex.: crise de qualidade/produção da Boeing (BA), problemas regulatórios de
um banco específico, resultado trimestral surpreendente de uma varejista).

**Conclusão pronta:** "A partir do PC4/PC5, o modelo já está descrevendo ruído
específico de empresa, não mais um fator de mercado amplo — é aqui que a curva do
gráfico de variância (scree plot) tipicamente 'achata', sinalizando que componentes
adicionais adicionam pouca informação nova por unidade de complexidade."

---

## 3. Como o "número de componentes" muda a história que você conta

| nº de PCs usados no K-Means | O que essa escolha significa na prática | Conclusão para apresentar |
|---|---|---|
| **2** | Você força o K-Means a agrupar usando só "mercado geral" (PC1) + "crescimento vs. defensivo" (PC2). Simples de visualizar, mas ignora energia, industriais etc. | "Com apenas 2 componentes, cerca de 40–55% da variância é usada — os clusters já separam bem 'tech/IA' de 'defensivas', mas empresas de energia e industriais tendem a ficar mal classificadas, misturadas em grupos que não fazem sentido econômico." |
| **3–5** (padrão do app: 5) | Captura mercado geral + growth/value + energia/commodity + 1–2 fatores mais sutis (ex.: sensibilidade a juros dos bancos, exposição a tarifas de importação). Normalmente soma **65–80%** da variância. | "Com 5 componentes já conseguimos separar handeis claros: um cluster 'IA/crescimento', um cluster 'energia', um cluster 'defensivas de dividendo' e um cluster 'financeiro/cíclico sensível a juros' — batendo majoritariamente com a intuição econômica, mas cruzando a linha de setores oficiais em pontos específicos (ex.: Tesla se comportando mais como tech do que como automotiva)." |
| **8–10** (máximo do app) | Você começa a reconstruir quase toda a variância original (>85–90%), mas os componentes extras capturam principalmente ruído idiossincrático de uma ou duas empresas. Os clusters ficam mais fragmentados e menos interpretáveis. | "Aumentar para 8–10 componentes aumenta a variância explicada, mas não necessariamente melhora a qualidade dos clusters — o silhouette score tende a cair, porque o K-Means passa a reagir a ruído específico de empresa em vez de fatores de mercado amplos. Isso ilustra na prática o trade-off entre 'explicar mais variância' e 'manter clusters interpretáveis', central em redução de dimensionalidade." |

---

## 4. Como o "número de clusters (k)" muda a história

### k = 2 — "risco liga/desliga" (risk-on vs. risk-off)
Com poucos clusters, o K-Means costuma encontrar a divisão mais grosseira possível:
ações de alta volatilidade e beta alto (tecnologia, TSLA) de um lado, ações de baixa
volatilidade e beta baixo (consumo básico, saúde, telecom) do outro.

**Conclusão pronta:** "Com k=2 o modelo redescobre, sem nunca ter recebido rótulos de
setor, a dicotomia clássica de mercado 'risk-on vs. risk-off': um grupo de ações que
sobem mais forte em dias de otimismo (tech, consumo discricionário, industriais
cíclicos) e outro que serve de 'porto seguro' relativo (saúde, consumo básico,
telecom)."

### k = 3–4 (padrão do app: 4) — a granularidade "sweet spot"
Costuma ser o ponto onde o silhouette score é mais alto ou próximo do máximo, e onde
emergem os clusters mais fáceis de contar como história:

1. **"IA e crescimento"**: NVDA, AMD, MSFT, GOOGL, META, ORCL, CRM, ADBE — puxados
   pelo ciclo de investimento em infraestrutura de inteligência artificial e data
   centers de 2024–2026.
2. **"Energia/commodities"**: XOM, CVX, COP, SLB — movidos por preço do petróleo e
   risco geopolítico (Oriente Médio, guerra na Ucrânia, decisões da OPEP+), quase
   descolados do resto do mercado.
3. **"Defensivas/dividendo"**: KO, PEP, PG, WMT, JNJ, VZ, T, MRK — sensíveis
   principalmente à trajetória de juros do Federal Reserve, não ao ciclo de
   crescimento.
4. **"Financeiro/cíclico"**: JPM, BAC, GS, MS, WFC, AXP, C, junto com industriais
   como CAT, HON, GE — sensíveis a expectativas de corte/alta de juros e à saúde do
   crédito.

**Conclusão pronta:** "Com k=4 obtemos clusters que cruzam a classificação setorial
oficial em pontos muito específicos e explicáveis: por exemplo, se a Tesla (TSLA)
aparecer no cluster de 'IA/crescimento' em vez de junto da Ford (F) no cluster
cíclico/industrial, isso é consistente com a narrativa de mercado de que a Tesla é
precificada mais como uma aposta em IA/robótica/robotáxi do que como uma montadora
tradicional — enquanto a Ford permanece ligada ao ciclo automotivo clássico (crédito
ao consumidor, tarifas de importação de aço/alumínio, custo de peças)."

### k = 5–6 — separações mais finas dentro de setores "artificiais"
Nesse ponto o K-Means começa a dividir o próprio cluster de tecnologia — por exemplo,
separando "hardware/semicondutores" (NVDA, AMD, INTC) de "software/serviços em nuvem"
(MSFT, ORCL, CRM, ADBE), e pode isolar bancos de investimento mais expostos a
volatilidade de mercado (GS, MS) dos bancos comerciais tradicionais (WFC, JPM, BAC,
C, mais sensíveis ao ciclo de crédito ao consumidor).

**Conclusão pronta:** "Ao subir para k=5 ou k=6, o modelo revela subestruturas dentro
do próprio setor de tecnologia — semicondutores reagem mais forte e com mais
volatilidade a notícias específicas da cadeia de suprimentos de chips (ex.: export
controls dos EUA para a China, resultados da Nvidia), enquanto software/nuvem se
comporta de forma mais estável, mais parecida com 'crescimento de qualidade'."

### k ≥ 7 — superfragmentação
Perto do limite de 10 clusters para 40 empresas, você começa a formar clusters de 1–2
ações (frequentemente TSLA sozinha, ou BA sozinha por causa da crise de produção e
segurança da Boeing). O silhouette score tende a cair.

**Conclusão pronta:** "Clusters de k alto tendem a isolar empresas com eventos
totalmente idiossincráticos — por exemplo, a Boeing (BA) pode aparecer sozinha ou
quase sozinha em um cluster por causa da crise de qualidade/produção que a afeta desde
2024, um evento de empresa específica que nenhuma outra ação do universo compartilha.
Isso mostra o limite prático do K-Means: além de um certo k, ele para de encontrar
'fatores de mercado' e passa a isolar ruído."

---

## 5. Ganchos de narrativa "prontos para usar" (eventos reais 2024–2026)

Use esta tabela para justificar *por que* duas ações de setores diferentes podem cair
no mesmo cluster — verifique no seu resultado real se a correlação aparece, e cite o
evento como explicação causal plausível.

| Evento/tema macro real | Tickers potencialmente afetados juntos | Por que cruzam o setor "oficial" |
|---|---|---|
| Supercapex em infraestrutura de IA (data centers, GPUs) | NVDA, AMD, MSFT, GOOGL, META, ORCL | Todas se beneficiam do mesmo gasto de capital em IA, independente de serem "hardware" ou "software" |
| Guerra na Ucrânia + tensões no Oriente Médio → prêmio de risco no petróleo | XOM, CVX, COP, SLB | Risco geopolítico de oferta de energia afeta as quatro simultaneamente, descolando-as do resto do mercado |
| Ciclo de cortes/altas de juros do Federal Reserve | JPM, BAC, GS, MS, WFC, C, AXP + VZ, T (proxies de "bond") | Bancos (margem de crédito) e telecoms de alto dividendo (custo de oportunidade frente a títulos) reagem ao mesmo fator de juros |
| Tarifas de importação (aço, alumínio, autopeças, produtos chineses) | F, TSLA, CAT, BA, GE, WMT, NKE | Custos de insumos importados e cadeias de suprimento globais impactam montadoras, industriais e varejistas ao mesmo tempo |
| Boom de medicamentos GLP-1 (obesidade/diabetes) | LLY, PFE, MRK, JNJ, UNH | Reprecificação do setor de saúde em torno de uma única classe de medicamento, criando um subcluster dentro de "Saúde" |
| Crise de produção/segurança da Boeing | BA (isolada) e, em menor grau, GE (motores) e CAT/HON (fornecedores industriais) | Evento idiossincrático de uma empresa que "vaza" para fornecedores próximos na cadeia |
| Narrativa "Tesla = IA/robótica", não "Tesla = montadora" | TSLA aparecendo junto de NVDA/tech em vez de junto de F | Mercado precifica TSLA pela opcionalidade em robotáxi/IA, não pelos fundamentos de venda de carros |
| Consumo desacelerando / aperto do orçamento das famílias | WMT, PG, KO, PEP (defensivo) vs. MCD, NKE (mais cíclico/discricionário) | Separa "consumo essencial" de "consumo discricionário" dentro do mesmo setor oficial "Consumo" |

> **Importante para a apresentação:** apresente essas tabelas como *hipóteses
> testáveis com os dados do painel*, não como fatos absolutos. Diga algo como: "a
> literatura de mercado associa X a Y; nosso modelo mostra [confirma/não confirma]
> isso nos últimos 12 meses" — isso é academicamente muito mais defensável do que
> afirmar causalidade direta a partir de um clustering nao supervisionado.

---

## 6. Conclusões metodológicas (para a parte de "discussão" do trabalho)

- **PCA + K-Means não sabem o que é uma empresa.** Eles só veem números. Quando os
  clusters batem com a intuição econômica (ex.: "energia junta", "IA junta"), isso é
  evidência de que o mercado realmente precifica essas empresas por fatores de risco
  comuns — não é um artefato do algoritmo.
- **A classificação setorial "de manual" (GICS) é uma simplificação.** O trabalho
  mostra que o comportamento real de preço frequentemente obedece a fatores
  macroeconômicos (juros, geopolítica, ciclo de IA) que atravessam múltiplos setores
  — uma conclusão relevante para quem pensa em construir carteiras diversificadas.
- **O silhouette score nunca deve ser o único critério para escolher k.** Um k com
  score ligeiramente menor, mas que produz clusters interpretáveis e alinhados a
  eventos reais, é mais útil para uma análise de negócio do que o k "matematicamente
  ótimo" que fragmenta o resultado em grupos sem sentido econômico.
- **Poucos componentes = visão grosseira porém estável; muitos componentes = visão
  detalhada porém ruidosa.** Isso é o trade-off clássico de viés-variância aplicado à
  redução de dimensionalidade, e vale a pena nomear explicitamente esse paralelo na
  apresentação.
- **Resultados mudam com a janela de tempo.** Como o app sempre baixa "1 ano" a partir
  de hoje, rodar o mesmo código em datas diferentes pode dar clusters diferentes —
  isso não é um bug, é evidência de que as correlações de mercado são
  **regime-dependentes** (mudam conforme o contexto macro do momento), um ponto
  sofisticado para citar na conclusão do trabalho.

---

## 7. Checklist rápido para a apresentação

1. Rode o app com **k=2** e **2 componentes** primeiro → mostre a divisão
   risk-on/risk-off mais simples.
2. Suba para **5 componentes / k=4** (padrão do app) → identifique e nomeie os 4
   clusters com uma frase de causa real (tabela da seção 5).
3. Aponte pelo menos **uma ação que "traiu" seu setor oficial** (ex.: TSLA fora do
   grupo automotivo, ou GE fora do industrial) e explique com um evento real.
4. Mostre o **silhouette score** e explique por que o k escolhido é um equilíbrio
   entre "estatisticamente ótimo" e "interpretável para negócio".
5. Feche com a limitação: "correlação não é causalidade — o modelo mostra *que*
   empresas se movem juntas, a explicação de *por que* vem da nossa leitura do
   contexto macro, não do algoritmo".

