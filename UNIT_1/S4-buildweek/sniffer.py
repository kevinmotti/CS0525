import socket
import struct
from datetime import datetime

# configurazione
IFACE: str = "eth0"      # cambia in "wlan0" se sei su Wi-Fi, nel caso di test basati su connessione della VM
BUF_SIZE: int = 65535    # dimensione buffer per ricevere frame interi senza troncarli

def mac_addr(raw: bytes) -> str:
    # converte 6 bytes in formato MAC leggibile aa:bb:cc:dd:ee:ff
    return ":".join(f"{b:02x}" for b in raw)

def ipv4_addr(raw: bytes) -> str:
    # converte 4 bytes in IP leggibile xxx.xxx.xxx.xxx
    return ".".join(str(b) for b in raw)

# creo un raw socket a livello link-layer:
# AF_PACKET = layer 2 (Ethernet) su Linux, dà accesso "diretto" al device
# SOCK_RAW = raw frames completi in ricezione
# ntohs(3) = ETH_P_ALL -> cattura tutti i protocolli (tutto il traffico) 
s: socket.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))

# bind all'interfaccia (non obbligatorio, ma senza è più carico di risultati)
s.bind((IFACE, 0))

# log del momento di inizio, spiega come fermare lo sniffing
print(f"[{datetime.now().isoformat(timespec='seconds')}] sniffing su {IFACE} (CTRL+C per uscire)")

# provo a eseguire il blocco di codice
try:
    # creo un loop infinito
    while True:
        # frame: bytes grezzi del frame Ethernet 
        frame: bytes
        # addr: tupla “indirizzo” AF_PACKET (contiene info su interfaccia e tipo pacchetto)
        addr: tuple
        frame, addr = s.recvfrom(BUF_SIZE)

        # parsing header Ethernet: 14 bytes, suddivisi in:
        # dst_mac (6) | src_mac (6) | ethertype (2)
        # controllo che i byte siano davvero 14, per contenere l'header minimo
        if len(frame) < 14:
            continue

        # estrazione dell'header nei sottogruppi che lo compongono usando slicing
        dst_mac_raw: bytes = frame[0:6]
        src_mac_raw: bytes = frame[6:12]
        # EtherType è un intero unsigned a 16 bit in network byte order (big-endian).
        # "!" = network order (big-endian), così i 2 byte vengono interpretati come nello standard di rete
        # "H" = unsigned short (16 bit)
        ethertype: int = struct.unpack("!H", frame[12:14])[0]

        # recupero il timestamp a secondi usando la libreria datetime.
        ts: str = datetime.now().isoformat(timespec="seconds")
        # richiamo i metodi di conversione del mac in stringa
        dst_mac: str = mac_addr(dst_mac_raw)
        src_mac: str = mac_addr(src_mac_raw)

        # 0x0800 = IPv4, controllo che sia un IPv4 e che la lunghezza del frame sia superiore a header ethernet + header IPv4 minimi.
        if ethertype == 0x0800 and len(frame) >= 14 + 20:
            #recupero i byte dell'IP header minimo (20), partendo da quello dopo l'ultimo dell'header ethernet
            ip_header: bytes = frame[14:34]

            # primo byte: versione (4 bit) + IHL (4 bit)
            ver_ihl: int = ip_header[0]
            
            # IHL (Internet Header Length) è in gruppi da 32 bit (4 byte).
            # (ver_ihl & 0x0F) estrae i 4 bit bassi; *4 li converte in bytes.
            ihl: int = (ver_ihl & 0x0F) * 4
            # ip_header[9] = campo Protocol (1 byte): indica quale protocollo L4ISO/OSI è incapsulato
            proto: int = ip_header[9]
            # Indirizzi IPv4 sorgente/destinazione (4 byte ciascuno, estratti con slicing)
            src_ip: str = ipv4_addr(ip_header[12:16])
            dst_ip: str = ipv4_addr(ip_header[16:20])

            # se c'è abbastanza payload, provo a leggere porte TCP/UDP
            # TCP=6, UDP=17
            info_l4: str = ""
            # se il protocollo è TCP=6 o UDP=17 e la lunghezza del frame è maggiore a Ethernet(14)+IHL+prime due porte(2*2)
            if proto in (6, 17) and len(frame) >= 14 + ihl + 4:
                # primi 4 byte (l4) dopo header ethernet+IHL: src_port(2) + dst_port(2)
                l4: bytes = frame[14 + ihl: 14 + ihl + 4]
                # "!HH" = 2 unsigned short (16 bit) in network order
                src_port, dst_port = struct.unpack("!HH", l4)
                # stringa da appendere al log con porta sorgente -> porta destinazione
                info_l4 = f" ports {src_port}->{dst_port}"

            # Log “umano”: MAC, IPv4, protocollo L4 e (se presenti) porte.
            print(f"{ts} {src_mac} -> {dst_mac} IPv4 {src_ip} -> {dst_ip} proto={proto}{info_l4}")

        else:
            # Per EtherType diversi da IPv4 stampo un log minimale: tipo e lunghezza del frame.
            print(f"{ts} {src_mac} -> {dst_mac} ethertype=0x{ethertype:04x} len={len(frame)}")

except KeyboardInterrupt:
    # CTRL+C interrompe il loop senza stacktrace, passando al finally.
    pass
finally:
    # Eseguito sempre: chiudere il raw socket per rilasciare risorse.
    s.close()