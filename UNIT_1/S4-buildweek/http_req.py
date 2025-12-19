import requests

# definizione funzione:
# accetta una stringa (url) e non restituisce nulla (stampa a schermo i risultati)
def verifica_verbi_http(url: str) -> None:
    # lista dei verbi HTTP standard da testare (metodi)
    verbi: list[str] = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE']

    # stampa intestazione, \n per andare a capo dopo il titolo
    print(f"--- Analisi dei verbi HTTP per: {url} ---\n")

    # ciclo su ogni verbo della lista
    for verbo in verbi:
        try:
            # invio la richiesta scegliendo il metodo dinamicamente con requests.request
            # timeout=5: massimo 5 secondi di attesa (evita blocchi)
            # allow_redirects=False: non seguo redirect, così leggo il codice "nativo" della risorsa
            response: requests.Response = requests.request(
                verbo,
                url,
                timeout=5,
                allow_redirects=False
            )

            # estraggo lo status code HTTP
            code: int = response.status_code

            # descrizione testuale del codice, inizialmente vuota, viene valorizzata in base al codice numerico
            descrizione: str = ""

            # interpreto i codici più comuni per dare un output leggibile
            if code == 200:
                # 200: richiesta accettata e risorsa OK
                descrizione = "ACCETTATO (OK)"
            elif code == 405:
                # 405: metodo non permesso su quella risorsa (spesso indica che il server blocca quel verbo)
                descrizione = "NON PERMESSO (Method Not Allowed)"
            elif code == 403:
                # 403: il server rifiuta l’accesso (autorizzazioni)
                descrizione = "VIETATO (Forbidden)"
            elif code == 404:
                # 404: risorsa inesistente o nascosta
                descrizione = "RISORSA NON TROVATA"
            elif code == 401:
                # 401: autenticazione richiesta
                descrizione = "NON AUTORIZZATO"
            elif 300 <= code < 400:
                # 3xx: redirect (301/302/307/308...)
                descrizione = "REDIRECT"
            else:
                # qualunque altro codice meno comune lo metto qui
                descrizione = "Altro"

            # stampa formattata:
            # <10 e <8 servono per allineare le colonne
            print(f"{verbo:<10} | {code:<8} | {descrizione}")

        # intercetto errori generici di requests (timeout, DNS, connessione rifiutata, ecc.)
        except requests.exceptions.RequestException:
            # se fallisce, stampo ERR e una descrizione semplice
            print(f"{verbo:<10} | {'ERR':<8} | Errore di connessione")


# entry point: esegue solo se lancio questo file direttamente
if __name__ == "__main__":
    # input dell’utente (stringa) per la URL target
    target_url: str = input("Inserisci l'URL da testare (es. http://example.com): ")

    # se manca http:// o https:// lo aggiungo per evitare errori in requests
    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    # chiamo la funzione di test
    verifica_verbi_http(target_url)
