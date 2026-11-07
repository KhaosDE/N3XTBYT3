"""Logikprüfung aller Aufgaben (Grundkurs und Szenarien), Stand 07.11.2026.

Spielt jede Aufgabe bis zum Lösungsschritt durch und gibt dann
- eingebaute Tippfehler (Buchstaben vertauscht / einer fehlt, im Befehlsnamen, in einer Option, im Argument),
- echte Aliase der Windows PowerShell 5.1 (gsv, gci, dir, ri …),
- gleichwertige Schreibweisen (mit/ohne -Name)
ein und meldet, wie die Simulation reagiert. Aufruf im Projektordner:
    python werkzeuge/logikpruefung.py
Die Hinweis-Prüfung am Ende liefert viele Fehlalarme (Wörter in Anführungszeichen, Befehle auf
anderen Rechnern) und ist nur zum Durchsehen gedacht.
"""
import os, sys, re, json, tempfile, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["N3XTBYT3_DATEN"] = tempfile.mkdtemp()
from n3xtbyt3.kern.sitzung import Sitzung
from n3xtbyt3.kern.systeme import REIHENFOLGE
from n3xtbyt3.kern.szenario import lade_allgemein, lade_system
from n3xtbyt3.kern import grundkurs as gk

ALIAS = {  # Windows PowerShell 5.1, Get-Alias
 "get-service":["gsv"], "start-service":["sasv"], "stop-service":["spsv"],
 "get-process":["gps","ps"], "stop-process":["spps","kill"], "get-command":["gcm"],
 "get-childitem":["gci","dir","ls"], "set-location":["sl","cd","chdir"],
 "get-content":["gc","cat","type"], "get-location":["gl","pwd"], "new-item":["ni"],
 "copy-item":["cpi","copy","cp"], "move-item":["mi","move","mv"], "remove-item":["ri","del","rm","erase"],
 "clear-host":["cls","clear"], "get-help":["help"],
}
POSNAME = {"get-service","start-service","stop-service","restart-service","get-process","get-command","get-help"}

def typos(cmd):
    """Tippfehler im längsten Argument und im Befehlsnamen (Buchstaben vertauscht / einer fehlt)."""
    w = cmd.split()
    out = []
    def swap(s):
        idx = [i for i in range(len(s)-1) if s[i].isalpha() and s[i+1].isalpha() and s[i]!=s[i+1]]
        if not idx: return None
        i = idx[len(idx)//2]; return s[:i]+s[i+1]+s[i]+s[i+2:]
    def drop(s):
        idx = [i for i in range(1,len(s)-1) if s[i].isalpha()]
        if not idx: return None
        i = idx[len(idx)//2]; return s[:i]+s[i+1:]
    args = [(i,x) for i,x in enumerate(w[1:],1) if not x.startswith(("-","/")) and sum(c.isalpha() for c in x)>=4]
    if args:
        i,x = max(args, key=lambda t: len(t[1]))
        for f,art in ((swap,"Argument vertauscht"),(drop,"Argument Buchstabe fehlt")):
            y=f(x)
            if y: out.append((art, " ".join(w[:i]+[y]+w[i+1:])))
    opts = [(i,x) for i,x in enumerate(w[1:],1) if x.startswith("-") and len(x)>=5]
    if opts:
        i,x = opts[0]; y=swap(x[1:])
        if y: out.append(("Option vertauscht", " ".join(w[:i]+["-"+y]+w[i+1:])))
    if len(w[0])>=4:
        y=swap(w[0])
        if y: out.append(("Befehlsname vertauscht", " ".join([y]+w[1:])))
    return out

def bewertung(texte, typo_cmd, richtig):
    t = " ".join(texte)
    if re.search(r"Fast!|Meintest du|Schreibweise Zeichen|Tippfehler|Achte auf", t): return "erkannt"
    if "Prüfe Parameter und Schreibweise" in t or "nicht mit diesen Zusätzen" in t: return "allgemein"
    return "nicht erkannt"

ergebnisse = collections.defaultdict(list)   # Kategorie -> Liste
stat = collections.Counter()

def notiere(kat, ort, text):
    ergebnisse[kat].append(f"{ort}: {text}")

# ------------------------------------------------------------------ Grundkurs
for sid in REIHENFOLGE:
    allg = lade_allgemein(sid)
    kurs = gk.lade_kurs(sid, allgemein=allg)
    for f in kurs.fehler: notiere("Ladefehler", sid, str(f))
    for lek in kurs.lektionen:
        alle = [("mitmachen",i,s) for i,s in enumerate(lek.mitmachen)] + [("aufgaben",i,s) for i,s in enumerate(lek.aufgaben)]
        for pos,(teil,i,schritt) in enumerate(alle):
            ort = f"{lek.id} {teil} {i+1}"
            loes = schritt.loesung or [schritt.eingabe[0]]
            # Mitmachen: Vorgabe steht im Text?
            if teil=="mitmachen" and schritt.eingabe and schritt.eingabe[0] not in schritt.text:
                notiere("Mitmachen: Vorgabe fehlt im Anleitungstext", ort, f"Text „{schritt.text}“ / Vorgabe „{schritt.eingabe[0]}“")
            def bis_hier():
                lauf = gk.Lektionslauf(lek, allg)
                for (t2,i2,s2) in alle[:pos]:
                    for x in (s2.loesung or [s2.eingabe[0]]):
                        lauf.loesungsschritt(x)
                return lauf
            # Hinweis 3 / "Tippe:" in Hinweisen muss die Aufgabe lösen
            for h in schritt.hinweise:
                for m in re.finditer(r"Tipp[e]?:?\s+(.+?)(?:$|\s{2}|\s–|\s\(|\. )", h):
                    cmd = m.group(1).strip().rstrip(".").strip("`„“\"")
                    lauf = bis_hier()
                    la = None
                    for x in loes[:-1]:
                        if isinstance(x,str) and x!=loes[-1]: lauf.eingabe(x)
                    la = lauf.eingabe(cmd)
                    if not la.geschafft and len(loes)==1:
                        notiere("Hinweis nennt Befehl, der die Aufgabe nicht löst", ort, f"„{cmd}“ → {(la.tipp or ' '.join(z.text for z in la.antwort.zeilen))[:160]}")
            # Tippfehler am letzten Lösungsbefehl
            ziel = loes[-1]
            if isinstance(ziel,str):
                for art, tcmd in typos(ziel):
                    lauf = bis_hier()
                    for x in loes[:-1]: lauf.loesungsschritt(x)
                    la = lauf.eingabe(tcmd)
                    if la.geschafft: 
                        stat["gk akzeptiert"]+=1; notiere("Grundkurs: Tippfehler als richtig angenommen", ort, f"{art}: „{tcmd}“"); continue
                    texte = [z.text for z in la.antwort.zeilen] + [la.tipp or ""]
                    b = bewertung(texte, tcmd, ziel); stat[f"gk {b}"]+=1
                    if b!="erkannt":
                        notiere(f"Grundkurs: Tippfehler {b}", ort, f"{art}: „{tcmd}“ (richtig „{ziel}“) → {(la.tipp or texte[0] if texte else '')[:170]}")
                # Aliase / Name weglassen (nur Windows, ein Befehl)
                if sid.startswith("windows") and len(loes)==1:
                    w = ziel.split(); n=w[0].lower()
                    for a in ALIAS.get(n,[]):
                        lauf = bis_hier(); la = lauf.eingabe(" ".join([a]+w[1:]))
                        if not la.geschafft: notiere("Windows: echter Alias wird nicht angenommen", ort, f"„{' '.join([a]+w[1:])}“ statt „{ziel}“")
                    if n in POSNAME:
                        if len(w)==3 and w[1].lower()=="-name": alt=" ".join([w[0],w[2]])
                        elif len(w)==2 and not w[1].startswith("-"): alt=" ".join([w[0],"-Name",w[1]])
                        else: alt=None
                        if alt:
                            lauf=bis_hier(); la=lauf.eingabe(alt)
                            if not la.geschafft: notiere("Windows: gleichwertige Schreibweise (mit/ohne -Name) abgelehnt", ort, f"„{alt}“ statt „{ziel}“")
                    lauf=bis_hier(); la=lauf.eingabe(ziel.lower())
                    if not la.geschafft: notiere("Windows: Kleinschreibung abgelehnt", ort, f"„{ziel.lower()}“")

# ------------------------------------------------------------------ Szenarien
for sid in REIHENFOLGE:
    allg = lade_allgemein(sid)
    erg = lade_system(sid, allgemein=allg)
    for f in erg.fehler: notiere("Ladefehler", sid, str(f))
    for sz in erg.szenarien:
        loes = sz.loesung
        for k, ziel in enumerate(loes):
            if not isinstance(ziel,str): continue
            ort = f"{sz.id} Schritt {k+1}"
            def bis(k=k):
                s = Sitzung(sz, allg)
                for x in loes[:k]: s.loesungsschritt(x)
                return s
            for art,tcmd in typos(ziel):
                s = bis(); a = s.eingabe(tcmd)
                if a.art=="treffer":
                    stat["sz akzeptiert"]+=1; notiere("Szenario: Tippfehler als richtig angenommen", ort, f"{art}: „{tcmd}“ (richtig „{ziel}“) → {chr(32).join(z.text for z in a.zeilen)[:120]}"); continue
                texte=[z.text for z in a.zeilen]
                b = bewertung(texte,tcmd,ziel); stat[f"sz {b}"]+=1
                if b!="erkannt":
                    notiere(f"Szenario: Tippfehler {b}", ort, f"{art}: „{tcmd}“ (richtig „{ziel}“) → {' '.join(texte)[:170]}")
            if sid.startswith("windows"):
                w=ziel.split(); n=w[0].lower()
                for al in ALIAS.get(n,[]):
                    s=bis(); a=s.eingabe(" ".join([al]+w[1:]))
                    if a.art!="treffer": notiere("Windows: echter Alias wird nicht angenommen", ort, f"„{' '.join([al]+w[1:])}“ statt „{ziel}“")
                if n in POSNAME:
                    alt=None
                    if len(w)==3 and w[1].lower()=="-name": alt=" ".join([w[0],w[2]])
                    elif len(w)==2 and not w[1].startswith("-"): alt=" ".join([w[0],"-Name",w[1]])
                    if alt:
                        s=bis(); a=s.eingabe(alt)
                        if a.art!="treffer": notiere("Windows: gleichwertige Schreibweise (mit/ohne -Name) abgelehnt", ort, f"„{alt}“ statt „{ziel}“")
                s=bis(); a=s.eingabe(ziel.lower())
                if a.art!="treffer": notiere("Windows: Kleinschreibung abgelehnt", ort, f"„{ziel.lower()}“")
        # Hinweise mit Befehlen in Anführungen/Backticks: werden sie erkannt?
        for h in sz.hinweise:
            for m in re.finditer(r"[`„]([^`“]{3,80})[`“]", h):
                cmd=m.group(1)
                if not re.match(r"^[A-Za-z][\w.-]*(\s|$)", cmd): continue
                s=Sitzung(sz, allg); a=s.eingabe(cmd)
                if a.art=="unbekannt":
                    notiere("Szenario-Hinweis nennt Befehl, den die Simulation nicht kennt", sz.id, f"„{cmd}“")

print(json.dumps(stat, indent=1, ensure_ascii=False))
for kat, l in sorted(ergebnisse.items(), key=lambda t:-len(t[1])):
    print(f"\n### {kat} ({len(l)})")
    for x in l[:400]: print(" -", x)
