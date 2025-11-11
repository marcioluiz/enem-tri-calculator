"""
Command Line Interface for ENEM TRI Calculator

Provides an interactive CLI for users to calculate their estimated ENEM scores.
"""

import click
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from src.tri_calculator.calculator import TriCalculator
from src.models.exam_area import AreaType
from src.i18n import get_i18n

console = Console()

# Get locale from environment variable or use default
DEFAULT_LOCALE = os.getenv("ENEM_LOCALE", "pt-BR")

@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--locale", "--lang",
    type=click.Choice(["pt-BR", "en-US"], case_sensitive=False),
    default=DEFAULT_LOCALE,
    help="Interface language / Idioma da interface"
)
@click.pass_context
def cli(ctx, locale):
    """Calculadora ENEM TRI - Estime suas notas do ENEM / ENEM TRI Calculator - Estimate your ENEM scores"""
    # Store locale in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['locale'] = locale
    ctx.obj['i18n'] = get_i18n(locale)


@cli.command()
@click.option(
    "--use-yaml", "--yaml",
    is_flag=True,
    help="Use data from data/user_data.yaml file"
)
@click.option(
    "--mathematics", "-m",
    type=click.IntRange(0, 45),
    help="Number of correct answers in Mathematics"
)
@click.option(
    "--languages", "-l",
    type=click.IntRange(0, 45),
    help="Number of correct answers in Languages"
)
@click.option(
    "--natural-sciences", "-n",
    type=click.IntRange(0, 45),
    help="Number of correct answers in Natural Sciences"
)
@click.option(
    "--human-sciences", "-hs",
    type=click.IntRange(0, 45),
    help="Number of correct answers in Human Sciences"
)
@click.option(
    "--essay", "-e",
    type=click.FloatRange(0, 1000),
    help="Essay score"
)
@click.option(
    "--show-confidence/--no-confidence",
    default=False,
    help="Show confidence intervals for estimates"
)
@click.pass_context
def calculate(
    ctx,
    use_yaml: bool,
    mathematics: int,
    languages: int,
    natural_sciences: int,
    human_sciences: int,
    essay: float,
    show_confidence: bool
):
    """Calculate estimated ENEM scores based on correct answers."""
    i18n = ctx.obj['i18n']
    
    # Try to load data from YAML if requested
    if use_yaml:
        from src.data_collection.user_data_loader import UserDataLoader
        
        loader = UserDataLoader()
        if loader.load():
            is_valid, errors = loader.validate_current_year()
            
            if not is_valid:
                console.print("[red]Errors in YAML file:[/red]")
                for error in errors:
                    console.print(f"  - {error}")
                return
            
            # Use data from YAML
            current = loader.current_year
            mathematics = current.mathematics_correct
            languages = current.languages_correct
            natural_sciences = current.natural_sciences_correct
            human_sciences = current.human_sciences_correct
            essay = current.essay_score
            
            if i18n.locale == "pt-BR":
                console.print("\n[green]✓ Dados carregados de data/user_data.yaml[/green]\n")
            else:
                console.print("\n[green]✓ Data loaded from data/user_data.yaml[/green]\n")
        else:
            if i18n.locale == "pt-BR":
                console.print("\n[red]✗ Arquivo data/user_data.yaml não encontrado[/red]\n")
            else:
                console.print("\n[red]✗ File data/user_data.yaml not found[/red]\n")
            return
    
    # Prompt for values if not provided
    if mathematics is None:
        mathematics = click.prompt(i18n.t('prompts.mathematics'), type=int)
    if languages is None:
        languages = click.prompt(i18n.t('prompts.languages'), type=int)
    if natural_sciences is None:
        natural_sciences = click.prompt(i18n.t('prompts.natural_sciences'), type=int)
    if human_sciences is None:
        human_sciences = click.prompt(i18n.t('prompts.human_sciences'), type=int)
    if essay is None:
        essay = click.prompt(i18n.t('prompts.essay'), type=float)
    
    console.print(f"\n[bold cyan]{i18n.t('cli.calculating')}[/bold cyan]\n")
    
    # Determine the year to use
    target_year = 2024  # default
    
    # Try to get year from YAML if using --use-yaml
    if use_yaml:
        from src.data_collection.user_data_loader import UserDataLoader
        from src.models.exam_area import AreaType
        
        loader = UserDataLoader()
        if loader.load():
            if loader.current_year and loader.current_year.year:
                target_year = loader.current_year.year
    
    # Create calculator with INEP data (using determined year)
    calculator = TriCalculator(use_inep_data=True, reference_year=target_year)
    
    # Try to calibrate with user's historical data if available
    if use_yaml:
        if loader.use_historical_data() and loader.has_historical_data():
            # Calibrate each area with historical data
            calibrated_areas = 0
            
            # Extract years from historical data
            years_list = [year_data.year for year_data in loader.previous_years if year_data.year]
            
            for area_name, area_type in [
                ('mathematics', AreaType.MATHEMATICS),
                ('languages', AreaType.LANGUAGES),
                ('natural_sciences', AreaType.NATURAL_SCIENCES),
                ('human_sciences', AreaType.HUMAN_SCIENCES)
            ]:
                correct_list, scores_list = loader.get_historical_data_for_area(area_name)
                if len(scores_list) > 0:
                    calculator.calibrate_with_user_data(
                        area_type, 
                        correct_list, 
                        scores_list,
                        years_list
                    )
                    calibrated_areas += 1
            
            if calibrated_areas > 0:
                if i18n.locale == "pt-BR":
                    console.print(f"[dim]✓ Estimativa baseada em {len(loader.previous_years)} ano(s) de histórico pessoal[/dim]\n")
                else:
                    console.print(f"[dim]✓ Estimate based on {len(loader.previous_years)} year(s) of personal history[/dim]\n")
    
    # Calculate scores
    result = calculator.calculate_score(
        mathematics=mathematics,
        languages=languages,
        natural_sciences=natural_sciences,
        human_sciences=human_sciences,
        essay_score=essay
    )
    
    # Display results
    display_results(result, calculator, show_confidence, i18n)


def display_results(result, calculator, show_confidence: bool = False, i18n=None):
    """
    Display calculation results in a formatted table.
    
    Args:
        result: ExamResult object
        calculator: TriCalculator instance
        show_confidence: Whether to show confidence intervals
        i18n: I18n instance for translations
    """
    # Use default i18n if not provided
    if i18n is None:
        i18n = get_i18n()
    
    # Create results table
    table = Table(title=i18n.t('results.table_title'), show_header=True, header_style="bold magenta")
    
    table.add_column(i18n.t('results.column_area'), style="cyan", width=42)
    table.add_column(i18n.t('results.column_correct'), justify="center", style="yellow", width=9)
    table.add_column("Calculado", justify="right", style="green", width=10)
    table.add_column("Pessimista", justify="right", style="red", width=10)
    table.add_column("Otimista", justify="right", style="bright_cyan", width=10)
    
    # Add objective test results
    objective_areas = [
        (AreaType.MATHEMATICS, i18n.t('areas.mathematics'), 
         result.mathematics_calculated, result.mathematics_pessimistic, result.mathematics_optimistic),
        (AreaType.LANGUAGES, i18n.t('areas.languages'),
         result.languages_calculated, result.languages_pessimistic, result.languages_optimistic),
        (AreaType.NATURAL_SCIENCES, i18n.t('areas.natural_sciences'),
         result.natural_sciences_calculated, result.natural_sciences_pessimistic, result.natural_sciences_optimistic),
        (AreaType.HUMAN_SCIENCES, i18n.t('areas.human_sciences'),
         result.human_sciences_calculated, result.human_sciences_pessimistic, result.human_sciences_optimistic),
    ]
    
    for area_type, area_name, calculated, pessimistic, optimistic in objective_areas:
        area = result.areas[area_type]
        correct = f"{area.correct_answers}/45"
        calculated_str = f"{calculated:.1f}" if calculated is not None else "-"
        pessimistic_str = f"{pessimistic:.1f}" if pessimistic is not None else "-"
        optimistic_str = f"{optimistic:.1f}" if optimistic is not None else "-"
        
        row = [area_name, correct, calculated_str, pessimistic_str, optimistic_str]
        table.add_row(*row)
    
    # Add essay result
    essay_row = [i18n.t('areas.essay'), "-", f"{result.essay_score:.1f}", "-", "-"]
    table.add_row(*essay_row, style="bold")
    
    console.print(table)
    
    # Display summary statistics
    console.print()
    
    # Calculate averages for all three scenarios
    calculated_avg = None
    pessimistic_avg = None
    optimistic_avg = None
    
    if all([result.mathematics_calculated, result.languages_calculated, 
            result.natural_sciences_calculated, result.human_sciences_calculated]):
        calculated_avg = (
            result.mathematics_calculated + result.languages_calculated +
            result.natural_sciences_calculated + result.human_sciences_calculated
        ) / 4
    
    if all([result.mathematics_pessimistic, result.languages_pessimistic, 
            result.natural_sciences_pessimistic, result.human_sciences_pessimistic]):
        pessimistic_avg = (
            result.mathematics_pessimistic + result.languages_pessimistic +
            result.natural_sciences_pessimistic + result.human_sciences_pessimistic
        ) / 4
    
    if all([result.mathematics_optimistic, result.languages_optimistic,
            result.natural_sciences_optimistic, result.human_sciences_optimistic]):
        optimistic_avg = (
            result.mathematics_optimistic + result.languages_optimistic +
            result.natural_sciences_optimistic + result.human_sciences_optimistic
        ) / 4
    
    summary_text = ""
    if calculated_avg and pessimistic_avg and optimistic_avg:
        summary_text = (
            f"[bold]Média Objetiva Calculada:[/bold] [green]{calculated_avg:.1f}[/green]\n"
            f"[bold]Média Objetiva Pessimista:[/bold] [red]{pessimistic_avg:.1f}[/red]\n"
            f"[bold]Média Objetiva Otimista:[/bold] [bright_cyan]{optimistic_avg:.1f}[/bright_cyan]"
        )
    else:
        summary_text = (
            f"[bold]{i18n.t('results.average_score')}[/bold] [green]{result.average_score:.1f}[/green]\n"
            f"[bold]{i18n.t('results.objective_average')}[/bold] [green]{result.objective_average:.1f}[/green]"
        )
    
    summary = Panel(
        summary_text,
        title=f"[bold]{i18n.t('results.summary_title')}[/bold]",
        border_style="cyan"
    )
    console.print(summary)
    
    # Display disclaimer
    console.print()
    disclaimer = Text(
        f"⚠️  {i18n.t('disclaimer.warning')}\n"
        f"{i18n.t('disclaimer.official')}\n"
        f"{i18n.t('disclaimer.confidential')}",
        style="italic yellow"
    )
    console.print(Panel(disclaimer, border_style="yellow"))


@cli.command()
@click.option(
    "--use-yaml", "--yaml",
    is_flag=True,
    help="Use data from data/user_data.yaml file (current_year section must NOT be commented)"
)
@click.pass_context
def interactive(ctx, use_yaml: bool):
    """Interactive mode with step-by-step input."""
    i18n = ctx.obj['i18n']
    
    console.print(Panel.fit(
        f"[bold cyan]{i18n.t('cli.title')}[/bold cyan]\n"
        f"{i18n.t('cli.interactive_title')}",
        border_style="cyan"
    ))
    
    # Try to load from YAML if requested
    mathematics = None
    languages = None
    natural_sciences = None
    human_sciences = None
    essay = None
    
    if use_yaml:
        from src.data_collection.user_data_loader import UserDataLoader
        
        loader = UserDataLoader()
        if loader.load():
            # Try to load current year data if available and valid
            if loader.current_year is not None:
                is_valid, errors = loader.validate_current_year()
                
                if is_valid:
                    # Use data from YAML
                    current = loader.current_year
                    mathematics = current.mathematics_correct
                    languages = current.languages_correct
                    natural_sciences = current.natural_sciences_correct
                    human_sciences = current.human_sciences_correct
                    essay = current.essay_score
                    
                    if i18n.locale == "pt-BR":
                        console.print("\n[green]✓ Dados do ano corrente carregados de data/user_data.yaml[/green]")
                        console.print(f"  Matemática: [yellow]{mathematics}[/yellow] acertos")
                        console.print(f"  Linguagens: [yellow]{languages}[/yellow] acertos")
                        console.print(f"  Ciências da Natureza: [yellow]{natural_sciences}[/yellow] acertos")
                        console.print(f"  Ciências Humanas: [yellow]{human_sciences}[/yellow] acertos")
                        console.print(f"  Redação: [yellow]{essay}[/yellow] pontos\n")
                    else:
                        console.print("\n[green]✓ Current year data loaded from data/user_data.yaml[/green]")
                        console.print(f"  Mathematics: [yellow]{mathematics}[/yellow] correct")
                        console.print(f"  Languages: [yellow]{languages}[/yellow] correct")
                        console.print(f"  Natural Sciences: [yellow]{natural_sciences}[/yellow] correct")
                        console.print(f"  Human Sciences: [yellow]{human_sciences}[/yellow] correct")
                        console.print(f"  Essay: [yellow]{essay}[/yellow] points\n")
                else:
                    # Invalid data - show warning but allow interactive input
                    if i18n.locale == "pt-BR":
                        console.print("\n[yellow]⚠ Dados do ano corrente no YAML estão incompletos ou inválidos[/yellow]")
                        console.print("[dim]Digite os valores interativamente:[/dim]\n")
                    else:
                        console.print("\n[yellow]⚠ Current year data in YAML is incomplete or invalid[/yellow]")
                        console.print("[dim]Enter values interactively:[/dim]\n")
            else:
                # No current year data - show info message
                if i18n.locale == "pt-BR":
                    console.print("\n[cyan]ℹ Seção 'current_year' não encontrada no YAML[/cyan]")
                    console.print("[dim]Digite os valores interativamente (dados históricos serão usados para calibração):[/dim]\n")
                else:
                    console.print("\n[cyan]ℹ Section 'current_year' not found in YAML[/cyan]")
                    console.print("[dim]Enter values interactively (historical data will be used for calibration):[/dim]\n")
        else:
            if i18n.locale == "pt-BR":
                console.print("\n[red]✗ Arquivo data/user_data.yaml não encontrado[/red]")
                console.print("[dim]Digite os valores interativamente:[/dim]\n")
            else:
                console.print("\n[red]✗ File data/user_data.yaml not found[/red]")
                console.print("[dim]Enter values interactively:[/dim]\n")
    
    # If not using YAML, prompt for input
    if mathematics is None:
        console.print(f"\n[bold]{i18n.t('cli.input_prompt')}[/bold]\n")
    
    # Collect input
    areas_input = []
    areas_prompts = [
        i18n.t('areas.mathematics'),
        i18n.t('areas.languages'),
        i18n.t('areas.natural_sciences'),
        i18n.t('areas.human_sciences'),
    ]
    
    for area_name in areas_prompts:
        while True:
            try:
                value = click.prompt(
                    f"  {area_name} (0-45)",
                    type=int
                )
                if 0 <= value <= 45:
                    areas_input.append(value)
                    break
                else:
                    console.print(f"  [red]{i18n.t('prompts.range_error', min=0, max=45)}[/red]")
            except click.Abort:
                console.print(f"\n[yellow]{i18n.t('cli.cancelled')}[/yellow]")
                return
    
    # Essay score
    while True:
        try:
            essay = click.prompt(f"  {i18n.t('areas.essay')} (0-1000)", type=float)
            if 0 <= essay <= 1000:
                break
            else:
                console.print(f"  [red]{i18n.t('prompts.range_error', min=0, max=1000)}[/red]")
        except click.Abort:
            console.print(f"\n[yellow]{i18n.t('cli.cancelled')}[/yellow]")
            return
    
    # Calculate and display
    calculator = TriCalculator(use_inep_data=True, reference_year=2024)
    
    # Calibrate with historical data if using YAML
    if use_yaml:
        from src.data_collection.user_data_loader import UserDataLoader
        from src.models.exam_area import AreaType
        
        loader = UserDataLoader()
        if loader.load() and loader.use_historical_data() and loader.has_historical_data():
            # Calibrate each area with historical data
            calibrated_areas = 0
            
            # Extract years from historical data
            years_list = [year_data.year for year_data in loader.previous_years if year_data.year]
            
            for area_name, area_type in [
                ('mathematics', AreaType.MATHEMATICS),
                ('languages', AreaType.LANGUAGES),
                ('natural_sciences', AreaType.NATURAL_SCIENCES),
                ('human_sciences', AreaType.HUMAN_SCIENCES)
            ]:
                correct_list, scores_list = loader.get_historical_data_for_area(area_name)
                if len(scores_list) > 0:
                    calculator.calibrate_with_user_data(
                        area_type, 
                        correct_list, 
                        scores_list,
                        years_list
                    )
                    calibrated_areas += 1
            
            if calibrated_areas > 0:
                if i18n.locale == "pt-BR":
                    console.print(f"\n[dim]✓ Estimativa baseada em {len(loader.previous_years)} ano(s) de histórico pessoal[/dim]")
                else:
                    console.print(f"\n[dim]✓ Estimate based on {len(loader.previous_years)} year(s) of personal history[/dim]")
    
    result = calculator.calculate_score(
        mathematics=areas_input[0],
        languages=areas_input[1],
        natural_sciences=areas_input[2],
        human_sciences=areas_input[3],
        essay_score=essay
    )
    
    console.print()
    display_results(result, calculator, show_confidence=True, i18n=i18n)


@cli.command()
@click.pass_context
def info(ctx):
    """Display information about the TRI methodology and data sources."""
    i18n = ctx.obj['i18n']
    
    info_text = f"""
[bold cyan]{i18n.t('info.about_tri_title')}[/bold cyan]

{i18n.t('info.about_tri_desc')}

• [yellow]{i18n.t('info.tri_point_1')}[/yellow]
  {i18n.t('info.tri_point_1_desc')}

• [yellow]{i18n.t('info.tri_point_2')}[/yellow]
  {i18n.t('info.tri_point_2_desc')}

• [yellow]{i18n.t('info.tri_point_3')}[/yellow]
  {i18n.t('info.tri_point_3_desc')}

[bold cyan]{i18n.t('info.about_calculator_title')}[/bold cyan]

{i18n.t('info.about_calculator_desc')}
• {i18n.t('info.calc_point_1')}
• {i18n.t('info.calc_point_2')}
• {i18n.t('info.calc_point_3')}

[bold red]⚠️  {i18n.t('info.limitations_title')}[/bold red]
• {i18n.t('info.limitations_1')}
• {i18n.t('info.limitations_2')}
• {i18n.t('info.limitations_3')}

[bold cyan]{i18n.t('info.data_sources_title')}[/bold cyan]

{i18n.t('info.data_sources_url')}

{i18n.t('info.more_info')}
    """
    
    console.print(Panel(info_text, border_style="cyan", padding=(1, 2)))


@cli.command()
@click.argument("area", type=click.Choice(["mathematics", "languages", "natural_sciences", "human_sciences"]))
@click.argument("correct_answers", type=int)
@click.pass_context
def estimate_area(ctx, area: str, correct_answers: int):
    """Estimate score for a single area."""
    i18n = ctx.obj['i18n']
    
    if not 0 <= correct_answers <= 45:
        console.print(f"[red]{i18n.t('errors.invalid_range')}[/red]")
        return
    
    area_map = {
        "mathematics": (AreaType.MATHEMATICS, i18n.t('areas.mathematics')),
        "languages": (AreaType.LANGUAGES, i18n.t('areas.languages')),
        "natural_sciences": (AreaType.NATURAL_SCIENCES, i18n.t('areas.natural_sciences')),
        "human_sciences": (AreaType.HUMAN_SCIENCES, i18n.t('areas.human_sciences')),
    }
    
    area_type, area_display = area_map[area]
    
    calculator = TriCalculator()
    score = calculator.calculate_area_score(area_type, correct_answers)
    ci_lower, ci_upper = calculator.get_confidence_interval(area_type, correct_answers)
    
    console.print(f"\n[bold cyan]{area_display}[/bold cyan]")
    
    if i18n.locale == "pt-BR":
        console.print(f"Acertos: [yellow]{correct_answers}/45[/yellow]")
        console.print(f"Nota estimada: [green]{score:.1f}[/green]")
        console.print(f"Intervalo de confiança 95%: [bright_magenta][{ci_lower:.1f}, {ci_upper:.1f}][/bright_magenta]\n")
    else:
        console.print(f"Correct answers: [yellow]{correct_answers}/45[/yellow]")
        console.print(f"Estimated score: [green]{score:.1f}[/green]")
        console.print(f"95% Confidence interval: [bright_magenta][{ci_lower:.1f}, {ci_upper:.1f}][/bright_magenta]\n")


@cli.command()
@click.pass_context
def set_language(ctx):
    """Change interface language / Mudar idioma da interface"""
    from rich.prompt import Prompt
    
    console.print("\n[bold cyan]Select Language / Selecione o Idioma[/bold cyan]\n")
    console.print("1. Português (pt-BR)")
    console.print("2. English (en-US)")
    
    choice = Prompt.ask("\nChoice / Escolha", choices=["1", "2"], default="1")
    
    locale = "pt-BR" if choice == "1" else "en-US"
    
    # Set environment variable for future runs
    os.environ["ENEM_LOCALE"] = locale
    
    if locale == "pt-BR":
        console.print(f"\n[green]✓ Idioma alterado para Português[/green]")
        console.print("Para tornar permanente, execute:")
        console.print("[yellow]export ENEM_LOCALE=pt-BR[/yellow]\n")
    else:
        console.print(f"\n[green]✓ Language changed to English[/green]")
        console.print("To make it permanent, run:")
        console.print("[yellow]export ENEM_LOCALE=en-US[/yellow]\n")


if __name__ == "__main__":
    cli()
