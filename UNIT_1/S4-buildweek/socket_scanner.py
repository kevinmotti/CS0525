import socket
import json
from datetime import datetime

#definizione funzione:
#accetta una stringa (range di porte), restituisce una tupla di interi
def parse_range(range_str: str) -> tuple[int, int]:
    nospacestring = range_str.replace(" ", "") #rimuove spazi

    #se utente schiaccia invio per sbaglio, alza un errore
    if nospacestring == "":
        raise ValueError("Range vuoto. Inserisci una porta (es. 80) o un range (es. 20-100).")

    # Caso 1: porta singola, es. "80"
    if "-" not in nospacestring: #se non trova il separatore -
        port = int(nospacestring) #porta unica
        if port < 0 or port > 65535: #check sul range delle porte, se fuori range, alza un errore
            raise ValueError("La porta deve essere tra 0 e 65535")
        return port, port #output doppio per essere comunque supportato da run_scan()

    # Caso 2: range, es. "20-100", ha verificato presenza del separatore
    partedstring = nospacestring.split("-") #divide la stringa in sotto parti assegnate alla lista partedstring
    if len(partedstring) != 2: # controlla la lunghezza di partedstring, se è diversa da 2 (porta bassa+porta alta) ritorna errore
        raise ValueError("Formato range non valido. Usa ad es. 20-100 oppure 80")

#altrimenti restituisce le due porte e fa ulteriori verifiche
    low = int(partedstring[0])
    high = int(partedstring[1])

#controlla che non ci siano numeri negativi o che superino il numero totale delle porte
    if low < 0 or high < 0 or low > 65535 or high > 65535:
        raise ValueError("Le porte devono essere tra 0 e 65535")
    #controlla se le porte sono in ordine, se non lo sono, alza un errore, va fatto il reinserimento
    if low > high:
        raise ValueError("Range non valido: la porta iniziale è maggiore della finale")
    return low, high

#definizione metodo dello scan della porta
#accetto stringa, intero e decimale, restituisco una stringa tra "open"|"closed"|"filtered"
def scan_port_state(target: str, port: int, timeout_s: float) -> str:
    #creo il socket
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #setto il timeout al socket
    sckt.settimeout(timeout_s)
    #tento la connessione all'IP target, specificando la porta su cui procedere con TCP handshake
    try:
        code = sckt.connect_ex((target, port))
        #se la connessione va a buon fine, restituisco open
        if code == 0:
            return "open"
        
        # se la connessione non va a buon fine, e quindi viene rifiutata senza timeout, restituisco closed
        return "closed"

# in caso di nessuna risposta nei tempi, restituisco filtered in quanto non c'è rifiuto esplicito della connessione
    except socket.timeout:
        return "filtered"
    except OSError:
        # errori di rete vari li classifico come filtered, in quanto non c'è rifiuto esplicito della connessione
        return "filtered"
    #infine, a prescindere, chiudo il socket
    finally:
        sckt.close()

#definizione metodo di scan del range di porte
#accetta stringa, due interi, un decimale, restituisce una lista contenente dizionari
def run_scan(target: str, low: int, high: int, timeout_s: float) -> list[dict]:
    #creo la lista che accoglierà i risultati, dizionari con port/state
    results = []
    #preparo il ciclo, dato che range esclude il valore finale, aumento high di 1 per includerlo
    for port in range(low, high + 1):
        #salvo lo stato risultato del metodo scan_port_state
        state = scan_port_state(target, port, timeout_s)
        #aggiungo alla lista il dizionario di porta e stato
        results.append({"port": port, "state": state})
    # a fine ciclo, restituisco la lista dei risultati
    return results

#definizione di metodo che restituisce json per i report
#accetta in imput stringa, due interi, un decimale e una lista di dizionari, restituisce un dizionario
def build_report(target: str, low: int, high: int, timeout_s: float, results: list[dict]) -> dict:
    #costruisco una lista di porte aperte, una di chiuse e una di filtrate
    open_ports = []
    closed_ports = []
    filtered_ports = []
    #ciclo la lista dei risultati e, in base allo stato, li suddivido
    for r in results:
        if r["state"] == "open":
            open_ports.append(r["port"])
        elif r["state"] == "closed":
            closed_ports.append(r["port"])
        else:
            filtered_ports.append(r["port"])
    #ritorno un JSON contenente i seguenti dati
    return {
        "target": target,
        "range": {"low": low, "high": high},
        "timeout_s": timeout_s,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "scanned_ports": (high - low + 1),
            "open_ports_count": len(open_ports),
            "open_ports": open_ports,
            "closed_ports_count": len(closed_ports),
            "closed_ports": closed_ports,
            "filtered_ports_count": len(filtered_ports),
            "filtered_ports": filtered_ports
        },
        "results": results
    }

def main():
    # chiede input dell'IP su cui fare la scansione, rimuove eventuali spazi
    target = input("IP da scansionare: ").strip()
    # chiede in input il range delle porte, rimuove eventuali spazi
    portrange = input("Range porte (es. 20-100) o porta singola (es 80): ").strip()

    timeout_s = 0.9  # valore base, modificabile, possibilità di renderlo input utente

    #effettua controlli sulla validità delle porte, vedere r.7
    low, high = parse_range(portrange)

    #log dell'operazione
    print(f"Scannerizzo {target} da {low} a {high} (timeout {timeout_s}s)...")
    # scannerizzo il range di porte, vedere r.67
    results = run_scan(target, low, high, timeout_s)
    # costruisce il report, vedere r.81
    report = build_report(target, low, high, timeout_s, results)

    out_file = "scan_results.json"
    #w = write, crea il file, se già presente lo sovrascrive
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Output salvato in: {out_file}")
    print(f"Porte aperte trovate: {report['summary']['open_ports']}")

# entry point: esegue solo se lancio questo file direttamente
if __name__ == "__main__":
    main()
