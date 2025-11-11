# ENEM TRI Calculator

<div align="center">

![License](https://img.shields.io/badge/license-MIT-green) ![INEP Data](https://img.shields.io/badge/INEP%20Data-2004--2024-orange) ![Status](https://img.shields.io/badge/status-active-success)

**Calculadora de notas do ENEM baseada na Teoria de Resposta ao Item (TRI)**  
*Com dados históricos oficiais do INEP (21 anos de estatísticas)*

[Instalação](#-instalação) • [Uso](#-uso) • [Metodologia](#-metodologia) • [Exemplos](#-exemplos-práticos) • [FAQ](#-faq---perguntas-frequentes)

</div>

---

## Projeto

Este projeto estima as notas de um aluno no ENEM com base no número de acertos em cada área do conhecimento e na nota de redação. Utiliza modelos estatísticos baseados na Teoria de Resposta ao Item (TRI) e **dados oficiais do INEP** para fornecer estimativas próximas às notas oficiais.

### Recursos

- **Dados Oficiais INEP**: Estatísticas de 2004 a 2024 (21 anos de histórico)
- **Três Cenários de Estimativa**: Pessimista, Calculado e Otimista
- **Calibração Personalizada**: Use seus resultados anteriores para melhorar a precisão
- **Suporte Multilíngue**: Interface em Português (pt-BR) e Inglês (en-US)
- **Configuração YAML**: Carregue dados históricos de arquivo de configuração
- **API Programática**: Use como biblioteca Python em seus projetos

### Áreas de Conhecimento

- **Matemática e suas Tecnologias** (45 questões)
- **Linguagens, Códigos e suas Tecnologias** (45 questões)
- **Ciências Humanas e suas Tecnologias** (45 questões)
- **Ciências da Natureza e suas Tecnologias** (45 questões)
- **Redação** (0-1000 pontos)

## Índice

- [Instalação](#-instalação)
- [Uso](#-uso)
  - [Interface CLI](#interface-de-linha-de-comando-cli)
  - [Suporte Multilíngue](#-suporte-a-múltiplos-idiomas)
  - [Uso Programático](#-exemplo-de-uso-programático)
- [Metodologia](#-metodologia)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Configuração YAML](#-configuração-do-yaml)
- [Testes](#-testes)
- [Internacionalização](#-internacionalização-i18n)
- [Utilitários](#️-utilitários)
- [Recursos Avançados](#-recursos-avançados)
- [Exemplos Práticos](#-exemplos-práticos)
- [FAQ](#-faq---perguntas-frequentes)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Conda (Anaconda ou Miniconda)

### Configuração

**1. Clone o repositório:**
```bash
git clone <repository-url>
cd enem-tri-calc
```

**2. Crie um ambiente conda:**
```bash
conda create -n enem-tri python=3.11
conda activate enem-tri
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Verifique a instalação:**
```bash
pytest tests/ -v
python main.py --help
```

## 💻 Uso

### Interface de Linha de Comando (CLI)

#### 1. Modo de Cálculo Direto

Especifique os valores diretamente na linha de comando:

```bash
python main.py calculate -m 35 -l 40 -n 38 -hs 42 -e 900
```

Ou deixe o programa solicitar os valores interativamente:

```bash
python main.py calculate
```

#### 2. Modo com Dados do YAML

Carregue seus dados do arquivo `data/user_data.yaml`:

```bash
python main.py calculate --use-yaml
```

Ou no modo interativo:

```bash
python main.py interactive --use-yaml
```

> **Dica**: O modo YAML automaticamente calibra as estimativas usando seus resultados anteriores!

#### 3. Modo Interativo

Interface passo a passo:

```bash
python main.py interactive
```

#### 4. Informações sobre TRI

Documentação sobre a metodologia:

```bash
python main.py info
```

#### 5. Estimar Nota de uma Área Específica

```bash
python main.py estimate-area mathematics 35
python main.py estimate-area languages 40
python main.py estimate-area natural_sciences 38
python main.py estimate-area human_sciences 42
```

### Suporte a Múltiplos Idiomas

O sistema suporta português (pt-BR) e inglês (en-US):

```bash
# Português (padrão)
python main.py --locale pt-BR calculate

# Inglês
python main.py --locale en-US calculate
```

Ou defina a variável de ambiente permanentemente:

```bash
export ENEM_LOCALE=en-US
python main.py calculate
```

Comando interativo para mudar idioma:

```bash
python main.py set-language
```

### Exemplo de Uso Programático

```python
from src.tri_calculator.calculator import TriCalculator
from src.models.exam_area import AreaType

# Criar calculadora com dados INEP do ano de 2024
calculator = TriCalculator(use_inep_data=True, reference_year=2024)

# Calcular notas baseadas no número de acertos
result = calculator.calculate_score(
    mathematics=35,
    languages=40,
    natural_sciences=38,
    human_sciences=42,
    essay_score=900
)

# Acessar resultados - Três cenários disponíveis
print(f"Matemática (Calculado): {result.mathematics_calculated:.1f}")
print(f"Matemática (Pessimista): {result.mathematics_pessimistic:.1f}")
print(f"Matemática (Otimista): {result.mathematics_optimistic:.1f}")

# Calcular média objetiva
print(f"Média Objetiva: {result.objective_average:.1f}")
print(f"Média Geral (com redação): {result.average_score:.1f}")
```

#### Calibração com Dados Históricos

```python
from src.data_collection.user_data_loader import UserDataLoader

# Carregar dados do usuário
loader = UserDataLoader()
if loader.load() and loader.has_historical_data():
    # Calibrar cada área com histórico pessoal
    for area_name, area_type in [
        ('mathematics', AreaType.MATHEMATICS),
        ('languages', AreaType.LANGUAGES),
        ('natural_sciences', AreaType.NATURAL_SCIENCES),
        ('human_sciences', AreaType.HUMAN_SCIENCES)
    ]:
        correct_list, scores_list = loader.get_historical_data_for_area(area_name)
        if len(scores_list) > 0:
            years_list = [y.year for y in loader.previous_years]
            calculator.calibrate_with_user_data(
                area_type, correct_list, scores_list, years_list
            )
    
    print(f"✓ Calibrado com {len(loader.previous_years)} anos de histórico")
```

## Metodologia

### Como Funciona

A estimativa de notas utiliza uma abordagem multinível:

1. **Estatísticas INEP Oficiais** (2004-2024)
   - Carrega dados de 21 anos de ENEM
   - Calcula médias, desvios-padrão, mínimos e máximos por área
   - Usa dados do ano de referência especificado (padrão: 2024)

2. **Três Cenários de Estimativa**
   - **Pessimista**: Limite inferior do intervalo de confiança
   - **Calculado**: Estimativa principal baseada em modelo logístico/linear
   - **Otimista**: Limite superior do intervalo de confiança

3. **Calibração Personalizada** (Opcional)
   - Ajusta parâmetros usando resultados anteriores do usuário
   - Usa z-scores e fatores de conversão personalizados
   - Melhora precisão quando há histórico disponível

4. **Modelos Matemáticos**
   - Modelo logístico para estimativas gerais
   - Interpolação linear para casos extremos
   - Projeção de z-scores para ajuste temporal

### Precisão das Estimativas

- ✅ **Com calibração pessoal**: Desvio médio de ±20-30 pontos
- ⚠️ **Sem calibração**: Desvio médio de ±30-50 pontos
- 📊 **Intervalos de confiança**: 95% de probabilidade

⚠️ **Importante**: Esta é uma **estimativa educacional**. A nota oficial só pode ser calculada pelo INEP com os parâmetros exatos de cada questão (dificuldade, discriminação e acerto ao acaso).

## 📁 Estrutura do Projeto

```
enem-tri-calc/
├── src/
│   ├── models/                      # Modelos de dados
│   │   ├── exam_area.py            # AreaType enum e ExamArea dataclass
│   │   ├── exam_result.py          # ExamResult com 3 cenários
│   │   └── tri_parameters.py       # Parâmetros TRI
│   ├── tri_calculator/             # Algoritmos de cálculo
│   │   ├── calculator.py           # TriCalculator principal
│   │   ├── estimator.py            # TriEstimator por área
│   │   └── conversion_factors.py   # Fatores de conversão
│   ├── data_collection/            # Coleta e processamento de dados
│   │   ├── historical_data.py      # Carregador de estatísticas INEP
│   │   ├── microdata_processor.py  # Processador de microdados
│   │   ├── data_processor.py       # Processamento estatístico
│   │   └── user_data_loader.py     # Loader de dados do usuário (YAML)
│   ├── cli/                        # Interface de linha de comando
│   │   └── cli.py                  # Comandos Click com Rich
│   ├── utils/                      # Utilitários
│   │   ├── cache_cleaner.py        # Limpeza de __pycache__
│   │   ├── analyze_user_data.py    # Análise de dados pessoais
│   │   └── regenerate_microdata.py # Regenerar estatísticas
│   └── i18n.py                     # Sistema de internacionalização
├── locales/
│   ├── pt-BR/                      # Traduções em português
│   │   ├── cli.json
│   │   ├── models.json
│   │   └── calculator.json
│   └── en-US/                      # Traduções em inglês
│       ├── cli.json
│       ├── models.json
│       └── calculator.json
├── data/
│   ├── inep_stats/                 # Estatísticas INEP (2004-2024)
│   │   ├── stats_2004.json
│   │   ├── stats_2005.json
│   │   └── ... (21 arquivos)
│   ├── user_data.yaml              # Seus dados (não versionado)
│   └── user_data.example.yaml      # Exemplo de configuração
├── tests/                          # Testes unitários
│   ├── conftest.py
│   ├── test_tri_calculator.py
│   ├── test_tri_estimator.py
│   ├── test_user_data_loader.py
│   ├── test_exam_area.py
│   ├── test_exam_result.py
│   ├── test_i18n.py
│   └── test_cache_cleaner.py
├── main.py                         # Ponto de entrada principal
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

## Configuração do YAML

### Estrutura do Arquivo

Copie `data/user_data.example.yaml` para `data/user_data.yaml` e preencha com seus dados:

```yaml
# Ano corrente (apenas acertos)
current_year:
  year: 2025
  mathematics: 35
  languages: 40
  natural_sciences: 38
  human_sciences: 42
  essay_score: 900

# Anos anteriores (acertos + notas oficiais)
previous_years:
  - year: 2024
    mathematics:
      correct_answers: 30
      official_score: 650.5
    languages:
      correct_answers: 38
      official_score: 720.3
    natural_sciences:
      correct_answers: 35
      official_score: 680.7
    human_sciences:
      correct_answers: 40
      official_score: 750.2
    essay_score: 880

# Configurações
settings:
  use_historical_data: true
  show_comparison: true
  confidence_level: 0.95
```

## 🧪 Testes

Execute os testes unitários:

```bash
pytest tests/
```

Com relatório de cobertura:

```bash
pytest --cov=src tests/
```

Com saída detalhada:

```bash
pytest -v tests/
```

Rodar teste específico:

```bash
pytest tests/test_tri_calculator.py -v
```

## 🌍 Internacionalização (i18n)

O projeto possui suporte completo a múltiplos idiomas através de arquivos JSON estruturados:

### Idiomas Disponíveis

- 🇧🇷 **Português (pt-BR)** - Padrão
- 🇺🇸 **English (en-US)**

### Estrutura de Traduções

```
locales/
├── pt-BR/
│   ├── cli.json        # Mensagens da interface CLI
│   ├── models.json     # Nomes de áreas e campos
│   └── calculator.json # Mensagens do calculador
└── en-US/
    ├── cli.json
    ├── models.json
    └── calculator.json
```

### Uso Programático

```python
from src.i18n import get_i18n

# Obter instância i18n
i18n = get_i18n('pt-BR')

# Traduzir chave
message = i18n.t('cli.calculating')  # "Calculando notas..."

# Traduzir com parâmetros
error = i18n.t('prompts.range_error', min=0, max=45)
```

### Adicionar Novo Idioma

1. Criar pasta `locales/<codigo-idioma>/` (ex: `locales/es-ES/`)
2. Copiar arquivos JSON de referência (pt-BR ou en-US)
3. Traduzir o conteúdo mantendo as chaves
4. Adicionar código do idioma em `src/i18n.py` → `SUPPORTED_LOCALES`

## �️ Utilitários

### Limpar Cache Python

```bash
python -m src.utils.cache_cleaner
```

### Analisar Dados do Usuário

```bash
python -m src.utils.analyze_user_data
```

### Regenerar Estatísticas INEP

```bash
python -m src.utils.regenerate_microdata
```

Isso reprocessa todos os dados do INEP (2004-2024) e regenera os arquivos `stats_*.json`.

## 📈 Recursos Avançados

### 1. Estatísticas por Ano

O projeto inclui estatísticas oficiais do INEP de **21 anos** (2004-2024):

```python
from src.data_collection.historical_data import HistoricalDataCollector
from pathlib import Path

collector = HistoricalDataCollector(Path('data'))
stats_2024 = collector.load_inep_statistics(2024)

print(f"Matemática 2024 - Média: {stats_2024['mathematics']['mean']}")
```

### 2. Múltiplos Cenários

Todas as estimativas retornam três valores:

- **Pessimista**: -1 desvio padrão
- **Calculado**: Valor esperado
- **Otimista**: +1 desvio padrão

```python
result = calculator.calculate_score(35, 40, 38, 42, 900)
print(f"Matemática: {result.mathematics_pessimistic:.1f} - "
      f"{result.mathematics_calculated:.1f} - "
      f"{result.mathematics_optimistic:.1f}")
```

### 3. Calibração Avançada

Use z-scores e fatores de conversão personalizados:

```python
calculator.calibrate_with_user_data(
    area_type=AreaType.MATHEMATICS,
    correct_answers_list=[28, 30, 32],
    scores_list=[620.0, 650.5, 680.0],
    years_list=[2022, 2023, 2024]
)
```

### 4. Intervalos de Confiança

```python
# 95% de confiança
lower, upper = calculator.get_confidence_interval(
    AreaType.MATHEMATICS, 
    correct_answers=35,
    confidence=0.95
)
print(f"IC 95%: [{lower:.1f}, {upper:.1f}]")
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Processo recomendado:

1. **Fork** o projeto
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/enem-tri-calc.git`
3. **Crie uma branch**: `git checkout -b feature/minha-feature`
4. **Faça suas alterações** e adicione testes
5. **Execute os testes**: `pytest tests/`
6. **Commit**: `git commit -m 'feat: adiciona minha feature'`
7. **Push**: `git push origin feature/minha-feature`
8. Abra um **Pull Request**

### Áreas para Contribuição

- Adicionar novos idiomas
- Melhorar modelos estatísticos
- Adicionar mais testes
- Melhorar documentação
- Corrigir bugs
- Propor novas features

## Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## Exemplos Práticos

### Exemplo 1: Cálculo Rápido

```bash
# Calcular notas com valores diretos
python main.py calculate -m 35 -l 40 -n 38 -hs 42 -e 900
```

**Saída esperada:**

<div align="center">

| 📚 Área de Conhecimento | ✅ Acertos | 🎯 Calculado | 📉 Pessimista | 📈 Otimista |
|:------------------------|:----------:|:------------:|:-------------:|:-----------:|
| 📐 **Matemática e suas Tecnologias** | 35/45 | **705.3** | 675.8 | 734.8 |
| 📝 **Linguagens, Códigos e suas Tecnologias** | 40/45 | **730.5** | 700.2 | 760.8 |
| 🧪 **Ciências da Natureza e suas Tecnologias** | 38/45 | **690.7** | 660.4 | 721.0 |
| 🌍 **Ciências Humanas e suas Tecnologias** | 42/45 | **750.2** | 720.5 | 779.9 |
| ✍️ **Redação** | - | **900.0** | - | - |
</div>

**📊 Resumo das Médias Objetivas**

<div align="center">

| Cenário | Média | Interpretação |
|:--------|:-----:|:--------------|
| 📈 **Otimista** | 749.1 | Melhor caso possível |
| 🎯 **Calculado** | 719.2 | Estimativa principal |
| 📉 **Pessimista** | 689.2 | Pior caso possível |

</div>

> 💡 **Dica**: A diferença de ~60 pontos entre os cenários representa o intervalo de confiança de 95%.

### Exemplo 2: Usando Dados do YAML

```bash
# 1. Copiar arquivo de exemplo
cp data/user_data.example.yaml data/user_data.yaml

# 2. Editar com seus dados
nano data/user_data.yaml  # ou vim, code, etc

# 3. Calcular com calibração automática
python main.py calculate --use-yaml
```

**Benefício**: Se você tiver 2+ anos de histórico, a precisão melhora significativamente!

### Exemplo 3: Modo Interativo em Inglês

```bash
export ENEM_LOCALE=en-US
python main.py interactive
```

### Exemplo 4: Comparar Diferentes Cenários

```python
from src.tri_calculator.calculator import TriCalculator

calculator = TriCalculator(use_inep_data=True, reference_year=2024)

# Cenário 1: Estudante A
result_a = calculator.calculate_score(30, 35, 32, 38, 800)

# Cenário 2: Estudante B
result_b = calculator.calculate_score(40, 42, 40, 43, 920)

print(f"Estudante A - Média: {result_a.average_score:.1f}")
print(f"Estudante B - Média: {result_b.average_score:.1f}")
print(f"Diferença: {result_b.average_score - result_a.average_score:.1f} pontos")
```

## FAQ - Perguntas Frequentes

### Por que as notas estimadas diferem das oficiais?

O ENEM usa parâmetros confidenciais para cada questão (dificuldade, discriminação, acerto ao acaso). Este projeto usa **estimativas estatísticas** baseadas em dados históricos agregados.

### Como melhorar a precisão?

1. ✅ Use o arquivo YAML com seus resultados anteriores
2. ✅ Quanto mais anos de histórico, melhor
3. ✅ Sempre compare os três cenários (pessimista, calculado, otimista)

### Posso confiar nas estimativas?

- **Com calibração pessoal**: Desvio médio de 20-30 pontos (bom indicador)
- **Sem calibração**: Desvio médio de 30-50 pontos (orientativo)
- Use como **referência**, não como valor absoluto

### O projeto usa dados oficiais?

✅ **Sim!** Todas as estatísticas vêm do INEP:
- 21 anos de dados (2004-2024)
- Médias, desvios-padrão, mínimos e máximos oficiais
- Atualizados anualmente

### Quais as limitações?

- ❌ Não tem acesso aos parâmetros de cada questão
- ❌ Não pode replicar exatamente o algoritmo do INEP
- ❌ TRI oficial usa informações não públicas
- ✅ Fornece estimativa estatisticamente fundamentada

## ⚠️ Disclaimer

Este projeto é **exclusivamente para fins educacionais e de estudo**. As estimativas fornecidas:

- ❌ **NÃO** substituem os resultados oficiais do INEP/MEC
- ❌ **NÃO** devem ser usadas para decisões formais
- ✅ **SÃO** úteis para orientação e planejamento de estudos
- ✅ **SÃO** baseadas em dados oficiais do INEP

Os parâmetros exatos das questões do ENEM (a, b, c da TRI) são **confidenciais** e não estão disponíveis publicamente.

## Contato e Suporte

- **Bugs**: Abra uma [issue](https://github.com/seu-usuario/enem-tri-calc/issues)
- **Sugestões**: Abra uma [discussion](https://github.com/seu-usuario/enem-tri-calc/discussions)

## 📄 Licença

Este projeto é licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### Atribuição

Dados estatísticos fornecidos por:
- **INEP** - Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
- **MEC** - Ministério da Educação

---

<div align="center">

**Desenvolvido com 🎓 para ajudar estudantes a entenderem melhor o sistema de avaliação do ENEM**

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!

</div>
