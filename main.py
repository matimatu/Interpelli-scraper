import asyncio
import json
from pathlib import Path

import typer
from telegram import Bot
from scraper import download_announces_html
from telegram_notifier import get_telegram_configuration,send_message
from data_structure import ResultsContainer

PROVINCES = ["SV","IM","SP","GE","ALL"]

app = typer.Typer(help="Scraper personale degli interpelli scolastici")


@app.callback()
def main():
    """Scraper personale degli interpelli scolastici."""
    pass


@app.command()
def run():
    """Esegue lo scraping di una sola fonte presente in config.json."""
    config_path = Path("config.json")
#  ------------------------------------- CONTROLLI INIZIALI -------------------------------------
    if not config_path.exists():
        typer.echo("ERRORE: config.json non trovato")
        raise typer.Exit(code=1)

    config = json.loads(config_path.read_text(encoding="utf-8"))

    if not config["sources"]:
        typer.echo("ERRORE: nessuna fonte di ricerca configurata in config.json")
        raise typer.Exit(code=1)
    
    for source in config["sources"]:
        if not source["class_code"]:
            typer.echo(f"nessuna classe di concorso configurata nella fonte {source}")
            raise typer.Exit(code=1)
    for province_code in source["province_codes"]:
        if  province_code not in PROVINCES:
            typer.echo(f"provincia ligure non valida nella fonte {source}")
            raise typer.Exit(code=1)
    #-------------------------------LOAD DATI ---------------------------------------
    basic_url_province = "https://servizi.istruzioneliguria.gov.it/provincia.php?as=2026%2F2027&stato=tutti"
    basic_url_region = "https://servizi.istruzioneliguria.gov.it/index.php?as=2026%2F2027&stato=tutti"
    tg_message = ""
    Path("output").mkdir(exist_ok=True)
    output_path = Path("output/interpelli.json")
    if output_path.exists() and output_path.stat().st_size > 0:
        dati = json.loads(output_path.read_text(
        encoding="utf-8"
        ))  
    else:
        dati = {
        "results": []
    }

    container_old_annunci = ResultsContainer.from_dict(dati)
    container_all_annunci = ResultsContainer.from_dict(dati)
    container_new_annunci = ResultsContainer()

    #-------------------------------------------------------------CICLO RICERCA INTERPELLI ------------------------------------------------------------------------
    class_code: str = ""
    for source in config["sources"]:
        # if class_code is not source["class_code"]:  #controllo se è cambiata la classe di concorso di ricerca
        class_code = source["class_code"]
        for province_code in source["province_codes"]: 
            url = (basic_url_province if province_code != "ALL" else basic_url_region ) \
            + "&" + "cdc=" +  class_code \
            + ("&p=" + province_code if province_code != "ALL" else "")
        
            typer.echo(f"Avvio scansione della fonte per la classe di concorso {class_code} \
                        in provincia {province_code} con url: {url}")

            link_annunci = asyncio.run(
                download_announces_html(url,class_code,province_code, headless=True)
            )#TODO in futuro da gestire in multithreading
            
            if not link_annunci:
                continue
            new_link_annunci = container_old_annunci.get_new_links(class_code,province_code,link_annunci)
         
            for link in new_link_annunci:
                container_new_annunci.add_link(class_code, province_code, link)
                container_all_annunci.add_link(class_code, province_code, link)

    tg_message = container_new_annunci.get_tg_message()
    if tg_message:
        bot_token, chat_id = get_telegram_configuration()
        bot = Bot(token=bot_token)
        asyncio.run(send_message(bot, chat_id, tg_message))
    
    json_string = container_all_annunci.to_json()
    Path("output").mkdir(exist_ok=True)
    output_path = Path("output/interpelli.json")
    with open(output_path, "w",encoding="utf-8") as f:
        f.write(json_string)

    typer.echo(f"Completato. Output: {output_path}")
    typer.echo(f"Trovati {container_all_annunci.count_links()} annunci.")
    if not tg_message:
        typer.echo(f"Nessun nuovo annuncio trovato, quindi nessun messaggio telegram mandato")
    else:
        typer.echo(f"di cui {container_new_annunci.count_links()} sono nuovi")


if __name__ == "__main__":
    app()