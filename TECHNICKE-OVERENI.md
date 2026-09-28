# Companion Auto Summon — rozsah ověření k 28. 9. 2026

## Aktuální kandidát 0.4.9 / 0.8.7

Externí název je **Companion Auto Summon for No Man's Sky**, s podpisem
**by Lineum Dynamics**. Herní krátký název, nastavení a pravidla vyvolávání
zůstávají zachované. Produkce 0.4.9 a menu 0.8.5-branding obsahují aktualizovaná
metadata; všech 14 katalogů má 41 položek včetně plného názvu a autorství.

Prošlo 333 produkčních a 675 vývojových testů bez chyb a vynechání, kontrola
skutečného frameworku mimo hru a obě nezapisující předstartovní kontroly.
Po drobné gramatické opravě korejského názvu znovu prošlo 24 lokalizačních testů
a framework i obě kontroly finálního balíčku `build/quick-menu-play-trial-087-r1`.
Ten obsahuje 40 datových souborů a manifest. Dne 28. 9. byl spuštěný po běžném
ukončení hry a ověřené záloze 46 souborů. V 11:07:26 se načetly oba módy a
dvanáct cílů; při první kontrole se nezměnily soubory balíčku ani předvolby a
paměť ručního výběru. Uživatel potvrdil viditelné vyvolání v Anomálii po
načtení i po výstupu z lodi; log potvrzuje dva přijaté požadavky a aktivní sloty.
Šlo o různé náhodné pety, takže to není důkaz opravy předchozího občasného
selhání. Pozorování jazyka uvedlo ENGLISH, bez zapnutí překladů. Podrobnosti
a neověřené oblasti zachovává [záznam 0.8.7](docs/research/LIVE-087.md).
Původní výstup `087` je překonaný. Dřívější 0.8.4 a připravená 0.8.6-r1 zůstávají neměnné.
Vážený výběr podle prostředí a shuffle jsou samostatný návrh, ne součást tohoto kandidáta.

## Historický výsledek 0.8.4 a příprava 0.8.5

Společná 0.8.4 byla 28. 9. 2026 spuštěna po ověřené záloze 43 souborů.
Načetly se oba módy a dvanáct nativních cílů; snímky potvrdily šest různých
ikon nastavení. Načtení v Anomálii nevedlo k viditelnému petovi. Hra krátce
hlásila aktivní slot, pozdější čtení už žádného aktivního ani čekajícího peta
nenašlo. Pozdější výstup z lodi ve stejné relaci úspěšně vyvolal jiného náhodného
peta. Příčina rozdílu zůstává neprokázaná; viz [záznam](docs/research/LIVE-084.md).

Zdrojová 0.4.8 / 0.8.5 ponechává diagnostiku i po prvním aktivním slotu až do
původního limitu 15 sekund / 4096 callbacků. Neopakuje vyvolání, nemění herní
pravidla ani texty a není nasazena. Běžící 0.8.4 se nemění.

## Původní příprava 0.8.4 — ochrana před neověřenou verzí

Spouštěče nyní ověřují zvolenou hru a před každou injekcí DLL znovu ověří
skutečný cílový proces. Neznámá nebo nečitelná verze, odlišná instalace,
neodpovídající framework, cizí rozšíření pyMHF a neúplný balíček start odmítnou.
Neprovádí se vynucené povolení, změna předvoleb ani zápis do savů.
Nativní ochrana před registrací hooků zůstává nezávislá.

Devět zpráv spouštěče má texty ve všech 14 katalozích; třináct překladů
zůstává neověřeným návrhem. Varování používá konzoli a případně dialog Windows,
nikoli neověřenou herní funkci. Jazyk vychází z Windows nebo explicitní volby.
Režim pouze pro ověření a volba bez dialogu žádné okno nezobrazují.
Katalogy nyní obsahují 39 klíčů; úplná lokalizace aplikace není dokončená.

Produkční automatika 0.4.7 a menu 0.8.3 jsou beze změn. Kandidát 0.8.4
nebyl spuštěn ve hře ani nasazen. Poslední instalace 0.8.2 a předchozí
nespuštěný balíček 0.8.3 zůstávají nedotčené. Ochrana runtime sama nepotvrzuje
bezpečnost budoucích vlastních technologií uložených v inventáři.

Finální zdroj prošel 329 produkčními a 633 vývojovými testy bez vynechání.
Společný balíček má 39 souborů a manifest. Skutečné pyMHF ověřilo načtení
obou tříd a šest voleb s dočasnými preferencemi, bez připojení ke hře a hooků.
Přímé kontroly přes Python i Windows PowerShell 5.1 uspěly nad existující hrou
a runtime bez spuštění či instalace. Opravena byla i chyba uvozovek v testovacím
příkazu staršího PowerShellu a zpracování cest se znaky mimo základní Unicode.

## Předchozí příprava 0.8.3 — ikony a jazykové katalogy

Samostatný nespuštěný balíček 0.8.3 zachovává produkci 0.4.7 beze změny a
přidává menu 0.8.3. Obsahuje sedm původních ikon, jasný popisek biomové volby
pro Random a stejná herní pravidla. Předchozí instalace 0.8.2 nebyla přepsána.
Prošlo 294 produkčních a 563 vývojových testů, včetně kontrol přiřazení ikon,
samostatného návratu k původní tlapce a odmítnutí neznámých cílových souborů.
Skutečné pyMHF ověřilo dvě třídy modů, 18 callbacků pro 12 cílů, společné
zpracování a všech šest nastavení v dočasných souborech. Bez připojení ke hře,
nativních hooků nebo změn osobních dat. Spouštěč prošel syntaktickou kontrolou.
Nezávislé dekódování všech šesti nových PNG/DDS párů potvrdilo shodné pixely
a průhlednost. V dočasné složce prošlo také sestavení z rozbaleného zdrojového
ZIP a spuštění jeho lokalizační kontroly; výsledný produkční soubor je shodný.

Všech 14 katalogů má 24 shodných klíčů; 13 překladů je označeno jako
neověřený návrh. Validator kontroluje aktuálnost, parametry a soulad s anglickým
menu i hláškami. Samostatné sestavení, společný balíček a vydání zdrojového ZIP
kontrolu vyžadují před zápisem. Testy potvrdily odmítnutí chybějícího překladu
bez přepsání předchozího výstupu. Nejde o herní podporu jazyků: detekce jazyka,
vykreslení znaků a pokrytí panelu i spouštěče zbývají.

## Předchozí spuštění 0.8.2

Při spuštění 0.8.2 se po ověřené záloze 43 souborů a opětovné kontrole hashů před startem načetly 27. 9. 2026 v 23:58:46 oba módy a 12 cílů, automatika ON. Všech 17 souborů i osobní nastavení zůstalo shodných. Textura byla připravená a její hash souhlasil; samotné vykreslení není potvrzené. Prošlo 294 produkčních a 519 vývojových testů. Dřívější 0.8.1 zastavila kontrola před startem: psutil nepojmenovalo chráněný proces Secure System. Opravený nativní výpis Windows ho rozpoznává a stále odmítá neúplné či chybné výsledky. Podklad: menu-play-0.8.2-startup.json. Herní přijetí čeká.

Soukromé testovací záznamy uvedené níže jménem souboru jsou uchované mimo Git repozitář a distribuční ZIP. Dokument obsahuje jejich shrnutí; osobní záznamy ani zálohy se nedistribuují.

## Spuštěný kandidát 0.4.7 / 0.8.2 — doplněný spouštěč

Před společným herním testem doplňuje spouštěč dvě oddělené ochrany proti
souběžnému startu. První drží PowerShell během přípravy prostředí a čekání
na hostitele, druhou používají obě varianty Python hostitele. Pojmenované
objekty Windows sdílejí i kopie v jiných složkách; existující objekt nový start
odmítne. Uvolnění se řídí životností handle, takže nezůstává soubor se starým PID.
Starší spouštěče tuto ochranu nemají a nesmějí běžet současně s novými.

Přepínač `-CheckOnly` kontroluje integritu balíčku, přesnou hru a již připravený
runtime i během hraní. Nic neinstaluje, nevytváří prostředí, nepřipravuje DDS
a nespouští hru ani hostitele. Chybějící runtime pouze ohlásí. Normální spuštění
při chybě zjišťování procesů skončí před přípravou prostředí.

Herní chování, nativní menu 0.8.0 a ikona se proti předchozímu kandidátu
nemění. Vše zůstává připravené pro jeden společný test. Běžící 0.7.1 i
nespuštěné 0.7.2 a 0.8.0 zůstávají zachované.

Prošlo **294 produkčních testů** a **519 vývojových testů**.
Samostatný test se skutečnými procesy Windows v izolovaném testovacím jmenném
prostoru ověřil odmítnutí druhého hostitele a uvolnění po řádném i náhlém
ukončení testovacího procesu. Nepoužil produkční zámek ani hru. Skutečné pyMHF
znovu prošlo kontrolou widgetů, obou módů, všech šesti nastavení i pořadí
zámek–kontrola–asset–spuštění–uvolnění se simulovaným startem. Následné skutečné
načtení módů je popsáno výše; viditelný výsledek a ovládání stále čekají na ověření.

## Starší připravený kandidát 0.4.6 / 0.8.0 — společný test

Rozšiřuje nativní stránku o všech šest dosavadních nastavení: automatiku,
poslední ruční nebo náhodný výběr, přednost shodného biomu a tři lokace.
Každý řádek používá původní frontu nastavení a ukládání produkčního runtime.
Otevření a navigace nic nemění. Potvrzení vyžaduje původní nativní akci,
stejnou položku a novou hranu stisku; opakované držení nemá opakovaně přepínat.
Zdrojové testy pokrývají celou stránku, ale skutečné ovládání ještě ověřené není.

Vlastní bílá tlapka s kruhovou šipkou je původní DDS o rozměru 256 × 256.
Budoucí spouštěč ji připraví pouze při zavřené hře na unikátní cestě v MODS;
ověří její hash, přesnou hru a odmítne neznámý existující soubor. Sestavení
balíčku nic neinstaluje. Nativní registrace se zkusí jednou při přirozeném
načítání prostředků menu. Vlastníkem držené reference zůstávají po dobu procesu.
Oba pozorované globální ukazatele správce prostředků musejí souhlasit; změna
nebo neshoda poskytovatele trvale vypne. Pozdější čtení nepoužívá starý ukazatel
menu. Pořadí je připravená vlastní textura, ověřená držená herní tlapka a nakonec
čistý text hlášky. Statická analýza a simulace nedokazují nativní životnost ani
skutečné načtení a vykreslení DDS.

Kandidát zachovává opravu původu ruční volby z 0.4.5 a potvrzení dlouhé 5,5 s.
Nemění pravidla vyvolávání, herní limity ani savy. Panel pyMHF zůstává dočasně
pro porovnání hodnot během společného testu. Běžící 0.7.1 a připravený 0.7.2
nebyly přepsány. Samostatný ZIP 0.4.6 obsahuje jen produkční část bez menu a DDS.

Prošlo **282 produkčních testů**: 192 runtime, 34 policy, 14 persistence,
24 settings a 18 launcher. Prošlo také **504 vývojových testů**, včetně
ověření selhání načtení ikony, původních herních návratových hodnot a instalace
assetu na dočasných cestách. Žádný test nečetl osobní nastavení ani herní savy.
Kontrola skutečného pyMHF ověřila osm widgetů, načtení obou módů a všech šest
voleb přes dočasné soubory původního runtime. Osmnáct callbacků sdílí 12 cílů;
společný cíl prošel oběma pořadími registrace a čtyřmi kombinacemi návratů
simulovaného originálu. Nativní hooky se neinstalovaly. Prošla také syntaxe
PowerShell spouštěče a vazba poskytovatele ikony.
Verze **0.4.6 / 0.8.0 ještě nebyla spuštěna ve hře**; žádný starší herní
výsledek se na ni nepřenáší.

## Starší připravený kandidát 0.4.5 / 0.7.2 — zatím nespouštěný

Nová ruční volba vyžaduje odpovídající nativní akci ovládání petů, přijetí
shodného požadavku a úspěšný návrat původní funkce. Identita, lokální hráč,
aplikace a kontext savu se znovu ověřují; po návratu se původní ukazatel položky
nečte. Nezařazené požadavky včetně obnovování řízeného hrou zruší čekající
automatiku, ale nepřepíší favorita ani neoznámí ruční volbu. Skutečný původ
staršího volání po aréně neznáme, proto dosavadní volbu automaticky nevracíme.

Krátká potvrzení výslovných změn mají 5,5 sekundy. `Companion saved.` znamená
úspěšné uložení; jinak se zobrazí `Companion selected (session only).` Podle
potřeby se doplní stav OFF nebo Random. Opakování stejné volby, automatické
vyvolávání a nativní obnovení zůstávají tiché. Statický rozbor doložil, že poslední
příznak původní funkce hlášek skrývá oba bloky ikony nezávisle na textu.
Kandidát jej zapíná se zachovaným ABI i vlastními buffery. Zmizelý bílý kruh
a čitelnost ještě musí potvrdit herní vizuální zkouška.

Prošlo **279 produkčních testů**: 189 runtime (26 nových), 34 policy,
14 persistence, 24 settings a 18 launcher. Dále prošlo **408 vývojových testů**,
skutečné pyMHF 0.2.4 / Dear PyGui se všemi osmi widgety a výsledný společný
balíček. Jeho devět produkčních a osm menu callbacků sdílí 11 různých cílů;
nový produkční pár používá stejný `TriggerAction` jako menu. Python registrace
a společné předávání callbacků prošly v obou pořadích a čtyřech kombinacích
Boolean výsledků, vždy s jediným voláním simulovaného originálu. Menu bylo při
tomto testu vypnuté; nativní hooky se neinstalovaly a hra se nepoužila. Prošlo
i dočasné nastavení přes společný můstek a syntaxe PowerShell spouštěče.

Verze 0.4.5 / 0.7.2 ještě nebyla spuštěna. Běžící 0.4.4 / 0.7.1 a starší
artefakty zůstávají beze změny; jejich výsledky níže se na kandidáta nepřenášejí.

## Dosavadní diagnostická verze 0.4.4 / 0.7.1

Pasivní sledování po přijetí požadavku nemění vyvolávání. Čte dosavadní nativní
údaje přes stávající callback, má limit 15 sekund, 4096 volání diagnostiky
a osm přechodových zpráv. Zmizení z fronty nezpůsobí opakování; aktivní slot
je údaj hry, nikoli důkaz viditelného peta. Při změně kontextu nebo zásahu hráče
sledování končí. Tato verze má jedno potvrzené vyvolání v Anomálii popsané níže;
bílý kruh neopravuje.
Po běžném ukončení hry a nové ověřené záloze 43 souborů se 0.7.1
spustil 27. 9. 2026 v 22:22:35. Načetly se oba módy a 11 hook cílů
s automatikou ON. Všech 14 payloadů, nastavení i paměť ruční volby
zůstaly při startu shodné. Registrace není ověřením viditelného vyvolání.
Podklady: `menu-play-0.7.1-startup.json` a příslušný záznam zálohy.

Kontroly 0.4.4 / 0.7.1 prošly: **253 produkčních testů** (včetně 23 nových případů diagnostiky), **408 vývojových testů** a ověření skutečného pyMHF i společného balíčku mimo hru. Testy nečetly osobní nastavení, nespouštěly hru a neregistrovaly herní hooky.

Jedno vyvolání v Random po načtení v Anomálii je pro 0.4.4 / 0.7.1 potvrzené. Dne 27. 9. 2026 log zaznamenal aktivaci načtením v 22:23:39.698, přijetí frontou v 22:23:42.250 (uváděných 2,56 sekundy) a očekávaného aktivního peta v 22:23:42.266 při první aktualizaci diagnostiky. Hráč potvrdil skutečné objevení. Nepředcházel výstup z lodi ani opakované vyvolání. Jde o jeden úspěšný běh; předchozí občasné selhání není tímto opravené, protože změna byla pouze diagnostická.

## Dílčí herní výsledek 0.7.0 a zjištěné chyby

### Pozdější hláška po aréně v 0.7.1

Hráč ohlásil „manual favorite saved“ po aréně, ale nedokáže určit spouštěcí
událost. Log v 22:35:48.366 zaznamenal přijetí slotu 2 a externí paměť módu
se v témže okamžiku změnila ze slotu 3 na slot 2 s jinou identitou. Nastavení
ON/Random zůstalo shodné. Hook verze 0.4.4 nerozlišuje původ přijatých požadavků
mimo vlastní automatické volání; skutečná ruční volba tedy není doložená.
Statický rozbor potvrzuje, že do stejné funkce vede i návrat peta z petího
souboje, ale původ konkrétního živého volání nebyl zachycen.

Omezené externí čtení přes query/read-only handle v 22:40:26 potvrdilo ve dvou
shodných snímcích lokaci 14, aktivní slot -1 a čekající slot -1. Pet v tomto
okamžiku nebyl evidovaný jako aktivní ani čekající; snímek neprokazuje jeho
stav v celém předchozím intervalu. Byla ověřena přesná binárka. Žádný zápis
do hry, runtime ani uložených preferencí diagnostika neprovedla.

Délka hlášky v této verzi je 3 sekundy a bílý kruh přetrvává. Později ověřený
příznak skrytí ikony je použit až v připravené 0.4.5. Podklady jsou v soukromém záznamu
`menu-play-0.7.1-arena-notice-observation.json`. Oprava přiřazení ruční volby,
čitelnosti a vykreslení zatím nebyla nasazená.

Hráč potvrdil vyvolání po výstupu při ON a pozdější potlačení při OFF.
Screenshot ukazuje OFF v položce menu i v herní hlášce; log potvrzuje předání
a použití změn. První popis pokusu s OFF je nejednoznačný: před prvním
zaznamenaným výstupem v 21:50:12 se stav znovu změnil na ON v 21:50:07.
Rychlé změny hráč výslovně vysvětlil opakovanými stisky. Nejde o ověření podržení,
přemapování, ovladače ani celého návratu a znovuotevření nabídky.

Po načtení v Anomálii se podle hráče pet neobjevil, přestože nativní fronta
přijala slot 2 v 21:49:21.727. Toto je neúspěšný viditelný výsledek, nikoli
ověřené vyvolání. Runtime po přijetí frontou ukončí požadavek a další aktivaci
peta už nesleduje. Přesná příčina uvnitř hry zatím není zjištěná. Samotná
nepřítomnost peta neopravňuje k opakování: mohla by následovat po ručním odvolání.

Screenshot zároveň poprvé potvrzuje vykreslení stavové hlášky. Nad textem je
nežádoucí bílý kruh. Volání předává ukazatel na nulový prostředek ikony, jehož
vizuální výsledek předtím nebyl ověřen. Záznam a screenshot jsou uchované jako
`menu-play-0.7.0-user-observation.json` a `menu-play-0.7.0-off-hud.png`.

## Připravený přepínač v nativním menu 0.7.0

Oddělený balíček 0.7.0 obsahuje nezměněný produkční skript 0.4.3 a první
skutečnou volbu menu: zapnutí/vypnutí automatického vyvolávání. Změna vyžaduje
nové potvrzení vyhodnocené samotnou hrou, shodnou vybranou položku a opětovnou
kontrolu po původním návratu nativní funkce. Podržení potvrzení, samotné
zobrazení nebo přestavba nabídky nesmějí změnu opakovat. Nepoužívá se pevná
fyzická klávesa. Neověřené cesty aktivace změnu neprovedou.

Prošlo **408 vývojových testů** a kontrola se skutečným pyMHF mimo hru:
dva módy, 15 callbacků pro 11 různých cílů, osm dočasných prvků panelu a žádná
vlastní klávesová zkratka. Test se skutečnou Python instancí produkčního módu
ověřil zařazení jedné změny, odmítnutí opakování a následné uložení jen do
dočasného nastavení. Ostatní volby zůstaly zachované. Herní funkce ani osobní
soubory test nepoužil. Nezměněná produkce zachovává svůj předchozí výsledek
230 testů; změna vývojového menu jejich nové spuštění nevyžadovala.

Balíček má 15 souborů, z toho 14 kontrolovaných payloadů. Po běžném ukončení
hry a nové hashově ověřené záloze 43 souborů byl spuštěn 27. 9. 2026.
V 21:48:38 se načetly oba módy a 11 hook cílů s automatikou ON. Všech 14
payloadů zůstalo shodných; počáteční kontrola potvrdila nezměněné nastavení
i paměť ruční volby. Registrace není ověřením funkčnosti přepínače.
Následuje zkouška OFF/ON, podržení, návratu/znovuotevření, pořadí
položek a běžných akcí petů. Ostatní nastavení zatím zůstávají v dočasném panelu;
z finálního hráčského rozhraní bude panel pyMHF odstraněn po dokončení menu.

## Jednorázové vyvolání po načtení ve verzi 0.4.3

Úspěšné načtení lokálního savu zaznamená jednu příležitost, pokud je automatika zapnutá. Během deserializace se nevolá vyvolání ani hledání místa. Následující aktualizace lokálního vlastnictví vyhodnotí povolené místo a původní nativní kontroly. Platí stejné čekání 1,5 sekundy a stejný odstup dvojic kontrol 0,5 sekundy. Nezavádí se nový hook ani neověřená paměťová adresa.

Uložený favorit se obnovuje podle úplné identity, nikoli podle starého slotu. Chybějící záznam při načítání se ověřuje nejvýše dvakrát za sekundu. Náhodný režim využívá stejný vhodný vlastněný soubor kandidátů. Příležitost ukončí již přítomný nebo čekající pet, ruční volba či náhled, nastoupení do lodi, změna nastavení nebo změna kontextu. Po přijatém vyvolání se nepřipravuje znovu při pouhé nepřítomnosti peta.

Nová 0.4.3 se v odděleném kombinovaném balíčku 0.6.2 načetla 27. září 2026 v 20:42:21. Log potvrdil automatiku ON a dva módy s deseti cíli hooků. Před spuštěním vznikla nová ověřená záloha všech 43 souborů profilu; soubory balíčku i dosavadní konfigurace zůstaly při následné kontrole shodné.

**Jedno automatické vyvolání po načtení pěšky na vesmírné stanici v režimu Random je potvrzené.** V 20:42:58.578 log zaznamenal příležitost po načtení savu a lokaci 2. Po čekání na nativní způsobilost vybral v 20:43:01.260 slot 1 z pěti vhodných vlastních petů a v 20:43:01.261 hra přijala požadavek. Uvedených 2,69 sekundy měří dobu do přijetí požadavku, nikoli přesnou dobu do viditelného objevení. Tomuto požadavku nepředchází aktivace výstupem z lodi; pozdější výstup v 20:44:27.717 je samostatnou událostí. Uživatel potvrdil skutečné objevení a upřesnil, že byl na stanici, nikoli v Nexusu. Všech dvanáct souborů běžícího balíčku zůstalo shodných. Důkaz je uchován v `menu-play-0.6.2-station-startup-success.json`.

Později ve stejné nezměněné relaci uživatel potvrdil jedno ruční odvolání bez opětovného objevení. Doporučený postup byl asi deset sekund zůstat pěšky; přesné místo, okamžik a délka pozorování nebyly nezávisle změřeny. Uživatel mezitím cestoval, takže nejde o kontrolovaný test odvolání bezprostředně po původním načtení na stanici. Soukromý záznam: `menu-play-0.6.2-manual-dismissal-success.json`.

Načtení na planetě nebo v Nexusu, režim poslední ruční volby po načtení, širší regrese ručního odvolání, preference biomu a multiplayer tím ověřeny nejsou.

Prošlo **230/230 testů módu**: 140 runtime, 34 policy, 24 settings, 14 persistence a 18 launcher. Dále prošlo 341 testů vývojových nástrojů, skutečné vytvoření osmi prvků panelu a kontrola společného načítání dvou tříd v pyMHF se 13 callbacky pro 10 různých cílů. Při těchto kontrolách se žádný hook neinstaloval do hry. SHA256 samostatného skriptu 0.4.3 je `87c4b8e44ec85605e5483542344c6addafd8d6ecb171cf0a7a365752419ad8dc`.

## Přejmenování ve verzi 0.4.2

Schválený název je **Companion Auto Summon**, repozitář `nms-companion-auto-summon`. Nový samostatný skript je `CompanionAutoSummon.py`, spouštěče `Launch-CompanionAutoSummon.py` a `Start-CompanionAutoSummon.ps1`, třída a současná záložka pyMHF `CompanionAutoSummon`. Herní pravidla, RVA, podpisy nativních funkcí, formáty uložených dat a výchozí nastavení zůstávají beze změny. Původní umístění `%LOCALAPPDATA%\NMS-AutoPet` pro preference, ruční volby a vývojový runtime zůstává kvůli kompatibilitě zachováno; samotné přejmenování osobní data nemigruje.

V době původního záznamu ještě kandidát 0.4.2 nebyl spuštěn; následný společný start s menu zaznamenává QUICK-MENU.md. Jeho vlastní offline výsledky zůstávají verzované. Níže uvedené výsledky a hash `AutoPet.py` patří výslovně starším verzím včetně 0.4.1; nepřejmenovávají se zpětně. Číslo 211 označuje historický počet testů 0.4.1, nikoli automaticky výsledek nové verze.

Přejmenovaná 0.4.2 prošla **212/212 offline testy**: 122 runtime, 34 policy, 24 settings, 14 persistence a 18 launcher. Nový regresní test ověřuje zachované preference a ruční volbu v původním datovém umístění. Kontrola skutečného pyMHF 0.2.4 / Dear PyGui 2.3.1 potvrdila jedinou třídu `CompanionAutoSummon` se zděděným `_mod_name`, osm widgetů, sedm callbacků pro šest cílů a nula hotkeys. Hooky nebyly registrovány, viewport nevznikl a hra se nespouštěla ani nepřipojovala. SHA256 vygenerovaného `CompanionAutoSummon.py`: `841c57ee82cd8fee7a4083a63eb846ee78bd6a8a23efcbbf5cef1b49fa96e472`.

## Historická evidence AutoPet do verze 0.4.1

## Co je doloženo

**Kandidát 0.4.1 prošel 211 offline testy a kontrolou všech osmi prvků nastavení se skutečným pyMHF 0.2.4 / Dear PyGui.** Nová preference biomu má staticky ověřené čtecí adresy a převod kategorií podle nativní hry. Načtení této verze do NMS ani výběr podle biomu ještě nejsou herně ověřené. Následující živé úspěchy patří výslovně uvedeným starším verzím.

**Ve verzi 0.4.0 je ověřené načtení, použití volby Random a jedno náhodné vyvolání vlastního peta na planetě.** Log dokládá výběr slotu 3 ze tří vhodných vlastních petů a přijatý požadavek; uživatel potvrdil skutečné objevení. Samostatné volby lokací, úplné ovládání panelu, nastavení po restartu a čekání na vhodné místo bez časového limitu včetně opakování odmítnutého požadavku zůstávají herně neověřené.

**Verze 0.3.3 úspěšně obnovila vybraného peta po restartu a automaticky ho vyvolala po výstupu z lodi na stanici.** Log zachytil obnovu a přijatý požadavek; uživatel navíc potvrdil skutečné objevení bez opětovného ručního výběru. Dřívější verze 0.3.2 stejně ověřila základní průchod na planetě. Závěr platí pro tyto dva vyzkoušené scénáře na stejném savu. Nexus, multiplayer, nevhodný terén, ovládání/HUD a dlouhodobá stabilita tím ověřeny nejsou.

Níže popsané mapování funkcí vzniklo statickým čtením NMS.exe ze souborového systému. SHA256 je uveden v manifestu. Po dokončení statických testů uživatel hru ukončil a povolil první runtime test; před ním vznikla ověřená záloha 42 souborů profilu. První spuštění přes framework skončilo výjimkou 0xc0000005 před vytvořením logu AutoPet. Funkčnost ve hře tím potvrzena nebyla.

NMS.py poskytlo podpisy existujících funkcí. V instalovaném EXE mají vzory Player.Update, OnEnteredCockpit, Spaceship.Eject, PlayerState.LoadFromData a QuickActionMenu.TriggerAction každý právě jednu shodu. Starý vzor konstruktoru PlayerCreatureOwnership má nula shod; tento konstruktor ani jeho struktura se nepoužívají.

Statická analýza větve `SummonPet` v rychlém menu a jejího volání v Player.Update dala následující mapu. Pojmenování nových pomocných funkcí je naše interpretace jejich použití; nejde o oficiální veřejné API hry.

| Funkce / hodnota | RVA nebo offset | Podklad |
|---|---:|---|
| Player.Update | RVA `0x1440CD0` | Jedinečná shoda NMS.py; načítá čekajícího peta a volá spawn cestu |
| Spaceship.Eject | RVA `0x17479D0` | Jedinečná shoda NMS.py |
| Player.OnEnteredCockpit | RVA `0x1479490` | Jedinečná shoda NMS.py |
| PlayerState.LoadFromData | RVA `0x56FA50` | Šest argumentů; skutečný návratový typ bool a druhý argument CommonStateData ověřeny v EXE |
| Kontrola vyvolání | RVA `0x146A410` | Přímé volání z větve rychlého menu, bool výsledek |
| Příprava požadavku vyvolání | RVA `0x146AC90` | Přímé volání z téže větve; uloží slot a data pro Player.Update |
| Globální ukazatel aplikace | RVA `0x6E7AAE8` | RIP-relative přístupy v těchto cestách |
| Lokální Player | app + `0x71C690` | Přímá adresa i shoda s accessor + Player offsetem |
| Lokace | app + `0x57A584` | Nativní kontrola vyvolání připouští 3/14/2; od verze 0.3.3 je používá i mód |
| Aktivní pet | app + `0x29A1C0` | Rychlé menu porovnává slot pro odvolání aktuálního peta |
| Čekající pet | player + `0x6010` | Zápis přípravy a čtení v Player.Update |
| CreatureSeed peta | app + `0xE10D0` + slot × `0x24A0` + `0x2330` | uint64; nativní kopie GcPetData.CreatureSeed |
| BirthTime peta | stejný záznam + `0x23C0` | uint64; obousměrná kopie GcPetData.BirthTime |
| Obsazenost slotu | stejný záznam + `0x2370` | Nativní kontrola vyvolání vyžaduje nenulový resource |
| SaveUniversalId | CommonStateData + `0x8980` | uint64; load i save kopírují přes PlayerState + `0x187E8` |
| PlayerNotifications.AddTimedMessage | RVA `0x9B8300` | Jedinečný vzor; 11 argumentů ověřených v těle i volajících funkcích |
| PlayerNotifications | app + `0x837B40` | Stejný offset v několika nativních volajících funkcích |

Větev rychlého menu čte akci z `MenuAction + 4` a slot z `+0x84`. Mod tuto neúplně popsanou strukturu nekopíruje ani znovu nepřehrává menu. Zachytává přijatý požadavek přípravy peta a později volá stejnou funkci na herním vlákně. Od verze 0.3.2 probíhá automatický přepočet a vyhodnocení po nativní aktualizaci vlastnictví petů; GUI a HUD zůstávají po Player.Update. Herní mechanismus nadále připravuje umístění a provádí samotné vyvolání.

Nativní kontrola zahrnuje index 0–29, obsazený slot a další vlastní podmínky hry. Mod její výsledek nemění. Kombinace CreatureSeed + BirthTime chrání před automatickým výběrem jiného peta po změně obsahu slotu.

## Persistence a přenositelnost

SaveUniversalId je trvalý údaj samotné hry: LoadFromData ho čte z CommonStateData + `0x8980` a zapisuje do PlayerState + `0x187E8`; zapisovací funkce RVA `0x576D60` provádí opačnou kopii. Návratová hodnota LoadFromData je bool, což bylo ověřeno také v jeho volajících funkcích. Ve 0.2 je tím opravena nepřesná deklarace prototypu 0.1 podle staršího NMS.py stuba. Verze 0.1 nebyla nainstalována ani spuštěna.

Pet loader `0x11FE4E0` kopíruje CreatureSeed z GcPetData + `0x128` do runtime + `0x2330` a BirthTime z + `0x148` do + `0x23C0`. Uložení provádí opačné kopie. Původně sledované runtime + `0x2390` je BoneScaleSeed; ten se pro trvalou identitu nepoužívá. Persistovaná identita je přesně 8 bajtů CreatureSeed a 8 bajtů BirthTime, bez strukturálního paddingu.

Po úspěšném lokálním načtení se přečte příslušná ruční volba z `%LOCALAPPDATA%\NMS-AutoPet\state.json`. V režimu poslední ruční volby se při následujícím výstupu z lodi prohledají obsazené sloty. Obnoví se pouze jediná shoda, takže přesun do jiného slotu nevadí a nejednoznačné shody nejsou odhadovány. JSON se zapisuje atomickou náhradou jen po přijatém ručním výběru; herní savy se neotevírají. Náhodný režim ve 0.4.0 dřívější ruční volbu nevyžaduje a náhodné losování tento soubor nepřepisuje.

SaveUniversalId je společné základnímu i expedičnímu kontextu jednoho savu. Implementace ukládá jednu volbu pro celý tento save a vždy ověřuje přítomnost peta v právě načteném kontextu.

Spouštěč a balíček používají relativní cesty, zjištěné Steam knihovny a složku aktuálního uživatele. Neobsahují konkrétní účet ani osobní save. Parametr GameDirectory ověřuje adresář, ale pyMHF nadále spouští app 275850 přes aktivní Steam. Skutečný EXE ještě znovu kontroluje vlastní mod před registrací hooků.

První pokus odhalil přesměrování uživatelského AppData přes Windows MSIX. Použitá verze pymem při načítání DLL vrací lokální adresu knihovny bez ověření výsledku vzdáleného LoadLibraryW. To odpovídá pozorovanému pádu, ale samotná shoda není důkaz příčiny. `Launch-AutoPet.py` předává kanonickou fyzickou cestu a místo předpokládané adresy vyžaduje právě jednu skutečně načtenou knihovnu se stejnou plnou cestou v cílovém procesu. Chybějící či neplatná adresa zastaví spuštění před voláním jejího kódu. Úprava platí jen pro hostitelský proces spouštěče; nainstalované soubory frameworku se nemění.

## Panel nastavení a potvrzení

PyMHF nabízí vlastní desktopové okno. AutoPet 0.4.1 má **osm GUI properties**: pět editovatelných `BOOLEAN` (automatika, Planets, Space stations, Nexus, Prefer same biome in Random mode), jeden `ENUM` (Companion selection: Last manually selected / Random) a dvě pouze čitelné `STRING` (Status, Companion). Výchozí hodnoty jsou zapnutá automatika, všechny tři lokace, `last_manual` a zapnutá preference biomu, která působí pouze v náhodném režimu na planetě. Status při čekání zobrazuje `Waiting for a suitable place`. Výzva k prvnímu ručnímu výběru platí pouze pro režim `last_manual`.

GUI setter pouze ukládá požadovanou změnu pod zámkem; změny se sloučí a volby na disk i volání hry provádí až hook lokálního Player.Update. Poslední změna konkrétní volby má přednost. Změna nastavení ruší předchozí čekající požadavek; zapnutí nebo změna režimu samo nevyvolává peta. Nejsou registrovány klávesové zkratky. Panel vyžaduje `pymhf[gui]==0.2.4`; launcher kontroluje přítomnost Dear PyGui i ve dříve vytvořeném prostředí.

Preference jsou oddělené od pojistky runtime chyby a ukládají se do `settings.json`, nikoli do souboru s výběry petů. Schéma 3 přidává Boolean `prefer_same_biome`; výchozí dokument je:

```json
{"schema":3,"enabled":true,"locations":[2,3,14],"selection_mode":"last_manual","prefer_same_biome":true}
```

Lokace jsou seřazená podmnožina celočíselných ID 2/3/14 bez duplicit; prázdný seznam je přípustný. Režimy jsou přesně `last_manual` a `random`. Schéma 1 zachová původní `enabled`, schéma 2 také lokace a režim; obě doplní novou preferenci jako true pouze v paměti. Samotné čtení soubor nepřepisuje. Schéma 3 vznikne až při výslovném uložení a již uložené false zůstává false. Kompatibilní pomocník `save(bool)` mění jen zapnutí a zachová ostatní preference. Neznámá pole, chybné typy včetně booleanu místo ID, duplicitní JSON klíče a soubor větší než 4 KiB jsou odmítnuty. Chybný existující soubor znamená výchozí OFF a případné výslovné přepnutí jen pro relaci. Zápis používá dočasný soubor, flush, fsync a atomickou náhradu; neplatná data se nepřepisují.

Nativní `AddTimedMessage` má v tomto EXE 11 argumentů: objekt, ukazatel na text, float trvání, ukazatel na RGBA, uint32 audio, ukazatel na resource ikony, bool, float prodleva a tři bool hodnoty. Starší NMS.py deklarace má nesprávný typ prodlevy a chybí jí poslední bool. Textový buffer má 512 bajtů, RGBA je výslovně zarovnána na 16 bajtů kvůli MOVAPS; prázdná ikona je platný ukazatel na int32(0). Audio 0 odpovídá INVALID_EVENT, nikoli chybovému zvuku.

Zprávy jdou pouze z lokálního Player.Update při kladném dt. Respektují nativní počet zpráv na `notifications + 0x28C` a potlačovací hodnotu na `app + 0x4BF50C`; při nepříznivém stavu čeká pouze nejnovější zpráva. Načtení jiného savu ji zruší. Nová ruční volba vytvoří jedno potvrzení; automatické vyvolání ani obnovení stejného peta ho nevytvářejí. Nativní void návrat není důkaz skutečného zobrazení.

## Ověření zdroje a testy

- Příkaz ze složky balíčku: `python -B -m unittest discover -s tests -v`. Výsledek společného běhu je zaznamenaný v manifestu.
- Sestavení `build.py` spojuje čtyři zdrojové části a syntakticky je kontroluje bez importu.
- Rozhodovací testy používají simulovaný čas a stav, bez herních souborů.
- Testy adaptéru používají vlastní paměťové bloky a náhrady frameworku a nativních funkcí. Prověřují směrování a pojistky, **nikoli skutečnou binární kompatibilitu**.
- Nezávislá kontrola zdroje pyMHF 0.2.4 potvrdila syntaxi dekorátorů, nativní volání s ASLR, formát samostatného skriptu a vyřazení `_disabled` tříd před registrací hooků.
- Po vlastním nativním volání se kontroluje čekající slot. Od 0.4.0 hodnota -1 ponechá tentýž výstup a téhož zvoleného peta pro další čerstvou dvojici kontrol umístění; přijatý slot čekání dokončí. Starší verze při -1 daný výstup přeskočily. Neočekávaný index po volání nebo výjimka v nativní cestě vypne automatiku. Obnovitelné chyby volitelného čtení biomu ve 0.4.1 pouze vracejí běžný náhodný výběr. Přijatý požadavek se nepovažuje za důkaz úspěšného zobrazení peta.
- Kontrola vyvolání RVA `0x146A410` kromě vlastnictví/kontextu volá pomocnou funkci umístění `0x507DF0`. První živý test odhalil chybějící přepočet interních dat bez otevřeného rychlého menu; oprava je popsána níže.
- Ve starší verzi se třemi GUI properties prošel jejich import a vytvoření také se skutečným nainstalovaným pyMHF 0.2.4 v odděleném Python prostředí. Proběhlo bez registrace hooků či spuštění hry; tím se nepotvrzuje runtime ABI.
- Pro 0.4.0 prošel oddělený offline test se skutečným pyMHF 0.2.4 a Dear PyGui: vzniklo všech sedm skutečných widgetů bez vytvoření zobrazovacího okna (viewportu), proběhly callbacky dropdownu ENUM i všech čtyř checkboxů a byl ověřen zápis schématu 2 do dočasného souboru. Framework nalezl sedm hook callbacků a nula hotkeys. Hooky nebyly registrovány, nedošlo k nativním herním voláním ani připojení ke hře. Jde o ověření konstrukce ovládacích prvků a jejich obsluhy; neprokazuje viditelnost panelu ve skutečné relaci, správnost ABI ani spawn.

## První živé spuštění

Po úpravě spouštěče druhé spuštění úspěšně načetlo AutoPet 0.3.1. Log potvrdil inicializaci frameworku, zapnutou automatiku a jeden mód s pěti nativními hooky. To ověřuje startovací cestu a registraci hooků; neprokazuje skutečný spawn, zobrazení potvrzení nebo multiplayer.

## Oprava umístění ve verzi 0.3.2

První vyvolání selhalo. Opakovaný výstup zachycený v 11:01:53 zapnul rozhodovací logiku; nativní způsobilost zůstala false do vypršení 12 sekund. Ruční výběr a jeho persistence fungovaly. Pozdější otevření náhledu mělo platné umístění, ale uživatel se mezitím přesunul, takže tento snímek není kontrolované porovnání stejného terénu.

Statická analýza prokázala, že aktualizace vlastnictví petů `0x5066A0` při zavřeném náhledu volá reset umístění `0x1439820`. Ten maže výsledek, transformace a kontext, ale neruší dva již inicializované úkoly testující kolize. Původní AutoPet pouze četl způsobilost a tento chybějící výpočet nespouštěl.

Nový callback běží po lokální `Ownership.Update(owner*, float dt)`. Objekt vlastnictví je `app + 0xE10D0`; jeho již zkonstruovaný objekt umístění je na `owner + 0x1B9140`. Po nativní kontrole vlastnictví/kontextu `0x505B70` volá běžný výpočet `0x1438040(arc*, float range1, float range2, uint32 hand)`. Oba dosahy čte z herní proměnné `base + 0x52381E0` a vyžaduje kladnou konečnou hodnotu. V této relaci byla 40.0; mód ji nenastavuje ani nezkracuje. Volba ruky přesně kopíruje nativní větev: výchozí 0, pokud bool funkce `0x60B770()` vrátí true, použije uint32 z `app + 0x30E7FC`.

První vlastní přepočet slouží k zahájení nových kolizních dotazů; jeho výsledek nelze použít pro vyvolání. Další aktualizace mohou zpracovat výsledky. Úplná nativní kontrola peta `0x146A410` a případné zařazení požadavku běží ve stejném callbacku, než by hra umístění opět vymazala. Náhled peta na `owner + 0x1B9300` nebo emote příznak na `owner + 0x1B937D` ruší automatický požadavek. Vypnutí, změna kontextu, přerušení způsobilých podmínek a nový výstup vyžadují nové připravení umístění.

Mód nevytváří vlastní kopii herního objektu, nepřepisuje platnost umístění, nepotlačuje reset a nevolá vykreslení náhledu. Při skončení čekání přestane výpočet volat; běžná hra provede úklid. Podrobná statická evidence je v pracovním `work/auto-pet-placement-audit/REPORT.md`.

Po nové ověřené záloze 42 souborů a ukončení předchozí hry se v 11:23:32 úspěšně načetla verze 0.3.2, jeden mód se šesti nativními hooky. Celkem prošlo 161 offline testů.

## Úspěšný základní herní test 0.3.2

Uživatel po restartu načetl stejný save a při prvním přistání na planetě vystoupil z lodi, bez nového ručního výběru peta. Log `pymhf-20260927T112332.log` ze dne 27. 9. 2026 zaznamenal:

- **11:27:37.264:** obnovení zapamatovaného peta ve slotu 1; v .265 aktivace čekání po výstupu.
- **11:27:38.546:** planetární stav pěšky (lokace 3), bez aktivního nebo čekajícího peta, nativní způsobilost false.
- **11:27:38.569:** nativní způsobilost true; zbývá dokončit souvislé čekání pěšky.
- **11:27:40.051:** jeden přijatý požadavek pro slot 1, 2,78 sekundy od výstupu.

V tomto běhu nepřibyl záznam nového ručního výběru. Uživatel výslovně potvrdil, že se pet skutečně objevil. Závěr se tedy opírá o log i herní pozorování, nikoli pouze o zařazení požadavku. Je tím potvrzena obnova volby mezi dvěma spuštěními a základní automatické vyvolání na planetě; nejde o ověření všech druhů petů či všech situací.

## Odstranění nadbytečného omezení ve verzi 0.3.3

Uživatel na stanici ověřil, že verze 0.3.2 peta automaticky nevyvolá. To odpovídalo našemu omezení pouze na planetu, ale nebylo to omezení samotné hry. Kontrola `0x505B70` výslovně přijímá lokace 2 (SpaceStation), 3 (PlanetOnFoot) a 14 (Nexus). Předchozí doporučení používat stanici jako zkoušku zakázaného místa bylo tedy nepřesné.

Verze 0.3.3 používá stejné tři přípustné lokace, přičemž nadále volá nativní kontrolu vlastnictví/kontextu, výpočet prostoru a úplnou kontrolu vyvolání. Neodemyká vyvolání tam, kde je hra odmítne. Označení Nexus je interní lokace 14; jiné interní označení Anomaly má hodnotu 15 a není automaticky přidáno. Freighter má lokace 9/10 a zůstává odmítnutý nativní kontrolou. Jeden test na stanici uspěl; výpočet ve všech interiérech tím potvrzený není.

Po běžném ukončení hry a nové ověřené záloze 42 souborů v 12:18:30 se verze 0.3.3 úspěšně načetla v 12:18:51, opět jako jeden mód se šesti nativními hooky. Prošlo 165 offline testů.

## Úspěšný herní test na stanici 0.3.3

Po restartu uživatel načetl stejný save a vyzkoušel výstup z lodi na stanici bez menu X a nového ručního výběru. Log `pymhf-20260927T121851.log` zachytil v **12:20:03.726** obnovení peta ve slotu 1 a aktivaci čekání, následně lokaci 2. V **12:20:05.031** byla nativní způsobilost true a v **12:20:05.243** hra přijala jediný požadavek po 1,52 sekundy od výstupu. Před tímto pokusem v nové relaci nepřibyl záznam ručního výběru.

Uživatel potvrdil skutečné objevení peta na stanici. Log a toto pozorování společně potvrzují obnovu volby po restartu a základní automatické vyvolání v této lokaci. Samotná existence požadavku by takový závěr nestačila podložit. Nexus zůstává neotestovaný.

## Změna čekání a volby peta ve verzi 0.4.0

Výchozí rozhodovací politika už nemá 12sekundovou expiraci. Výstup z lodi zůstává čekající, dokud hra nepřijme požadavek nebo nenastane událost, která ho zruší. Platforma archivu, nedostatek prostoru nebo dočasně nativně nepřípustná lokace samy čekání neukončí. Mód nepředpokládá, že konkrétní budova bude přijata; jakmile nativní kontroly dovolí první vhodné místo a skončí stabilizační prodleva, může dokončit původní výstup.

V podporované a uživatelem zapnuté lokaci zůstává podmínka 1,5 sekundy souvislého stabilního pobytu. V nativně nepřípustné lokaci se intent uchová, stabilita a rozpracovaný test místa se zahodí a nevznikají nativní volání umístění či vyvolání. Návrat do přípustné lokace tedy vyžaduje nové stabilní pozorování. Odlišná je podporovaná lokace vypnutá uživatelem: vstup do ní čekající výstup zruší a pozdější přechod jej sám neobnoví.

Kontrola umístění používá čerstvé dvojice callbacků po `Ownership.Update`. První pouze připraví nativní dotazy, druhý může vyhodnotit jejich výsledek. Druhý callback musí mít stejnou lokaci i nenulové ID fyzikálního kontextu hráče (`uint64` na `player + 0x2A8`) a navázat nejpozději za 0,25 sekundy. Při nulovém ID se nativní výpočet vůbec nevolá; změna ID vyžaduje nový pár. Starý nebo přerušený pár se pro vyvolání nepoužije. Mezi dokončenými páry je nejméně 0,5 sekundy, takže čekání nespouští úplnou kontrolu každým snímkem. Každý pokus používá původní herní dosah a nativní omezení. Mód nepřepisuje platnost místa ani nezkracuje herní limity.

Pokud příprava vyvolání vrátí čekající slot -1, politika uvolní právě probíhající pokus, ale ponechá exit intent a pevnou volbu. Další pokus vyžaduje nový pár kontrol po nejméně 0,5 sekundy. Přijatý požadavek ukončí daný výstup; mód potom nezkouší druhý spawn. Chybný či neočekávaný stav nadále vede ke zrušení nebo zastavení podle příslušné pojistky, nikoli k vynucenému vyvolání.

Čekání ruší vstup do lodi, ruční náhled peta nebo související emote, přijatý ruční výběr, skutečná změna nastavení, načítání savu, reset kontextu aplikace a změna identity již zvoleného peta. Přítomný či jiný nativně čekající pet rovněž ukončí původní výstup. Samotné načtení savu nebo zapnutí automatiky nový požadavek nevytváří.

Režim `last_manual` zůstává výchozí. Režim `random` může čekání zahájit i bez předchozí ruční volby: po přípravě místa vybere nejvýše jednoho vlastního peta z kandidátů přijatých nativními kontrolami. Vybraný slot a identita zůstanou pro daný výstup pevné včetně odmítnutého zařazení do fronty; čekání nikdy neslouží k opakovanému losování. Před zařazením se znovu ověří identita, obsazenost, vlastnictví a úplná způsobilost. Náhodný výběr nemění zapamatovaného ručního favorita. Po zrušení nevznikne náhradní los bez dalšího výstupu.

Tato část popisuje aktuální zdroj; rozsah živých výsledků je uveden níže. Verze 0.4.0 zatím nemá potvrzený průchod čekáním na archivu, přesunem na vhodné místo ani opakovaně odmítnutou frontou. Jeden základní průchod náhodným režimem na planetě již uspěl.

Finální sestavení 0.4.0 dne 27. 9. 2026 prošlo **197 offline testy** bez chyb a přeskočených případů: 109 runtime, 34 rozhodovací politika, 22 nastavení, 14 persistence a 18 spouštěč. Kontrolní součty zdrojů před a po běhu souhlasily. Sada zahrnuje simulované 300sekundové odmítání místa a následné vyvolání, opakování stejného peta po odmítnuté frontě, náhodný výběr bez přepsání favorita, zrušení nastavením a čerstvost kontrol při změně kontextu. Kontrola se skutečným pyMHF a Dear PyGui byla zopakována nad finálním vygenerovaným skriptem; potvrdila sedm vytvořených prvků a jejich volby bez registrace hooků či herních volání. Historické počty 161 a 165 výše patří verzím 0.3.2 a 0.3.3.

## Ověřené načtení runtime 0.4.0

Uživatel běžně ukončil herní relaci 0.3.3. Její spouštěč v terminálové relaci 31576 následně skončil s kódem 15; tato relace je historická a již neběží. Před nasazením 0.4.0 vznikla v 13:17:38 nová záloha 42 souborů profilu, se stabilním zdrojem a ověřenými kontrolními součty. Záznam: `backup-0.4.0-features-test.json`.

Po nasazení otestovaného balíčku byla hra spuštěna v 13:18:06 jako PID 4508. Log `pymhf-20260927T131811.log` v **13:18:11.299** potvrzuje AutoPet 0.4.0 se zapnutou automatikou a v **13:18:11.561** jeden načtený mód se šesti hooky. Uchovaná kopie: `runtime-0.4.0-startup.log`. Spouštěč této relace měl číslo 35396. Při pozdější kontrole v 13:59 již NMS neběžel; tento startovací záznam je historický.

Samotný start doložil pouze `runtime_load_verified`; následný herní výsledek je zaznamenán níže. Výběr podle biomu není součástí 0.4.0 a nebyl testován.

## Úspěšný náhodný výběr a vyvolání na planetě 0.4.0

Uživatel uvedl: „nastavil jsem náhodného peta a náhodný pet se objevil.“ Log stejné relace potvrdil v **13:22:49.680** použití nastavení `locations=[2,3,14]`, `selection=random`. V **13:24:28.249** obnovil zapamatovanou ruční volbu slotu 1 a v **13:24:28.250** aktivoval náhodný výběr pro výstup z lodi. V **13:24:29.549** vybral slot 3 ze tří způsobilých vlastních petů v planetární lokaci 3. V **13:24:31.108** hra přijala a zařadila požadavek slotu 3, po 2,86 sekundy od výstupu. Kopie: `runtime-0.4.0-random-success.log`.

Následný čtecí snímek runtime potvrdil zapnutou automatiku, režim `random`, `settings_ok=True`, aktivního peta v UI slotu 3, žádný nativní čekající slot (`-1`) a ukončený požadavek výstupu. Původní ruční favorit i jeho identita zůstaly v runtime zachované v interním slotu 0 (UI slot 1). Strukturovaný podklad a SHA256 logu: `random-success-0.4.0.json`.

Log společně s pozorováním a snímkem potvrzuje použití volby Random, jeden náhodný výběr, skutečné objevení peta na planetě a zachování ručního favorita v běžící relaci. Neprokazuje rovnoměrnost rozdělení ani opakované losování, všechny prvky GUI, zachování favorita na disku, zachování preferencí po restartu nebo vyvolání ručního favorita po přepnutí režimu.

## Preference domovského biomu ve verzi 0.4.1

Volba `prefer_same_biome` je výchozí zapnutá a působí pouze při prvním výběru peta v režimu Random na planetě (lokace 3). Nejdřív vznikne běžný seznam obsazených vlastních slotů, které prošly nativním vlastnictvím, přípravou umístění a úplnou kontrolou vyvolání. Pokud mezi nimi existují peti se známým shodným domovským biomem, losuje se rovnoměrně z této podmnožiny. Bez shody, při neznámém biomu nebo obnovitelné chybě čtení zůstává celý běžný seznam. Stanice, Nexus, ruční režim a vypnutá preference čtení biomu úplně vynechají. Jednou zvolený pet se při změně prostředí ani odmítnutí požadavku nepřelosuje.

Statická kontrola přesného podporovaného EXE doložila následující čtení; žádná nová nativní funkce se nevolá:

| Údaj | Ověřená adresa a typ |
|---|---|
| Domovský biom peta | `uint32` na `app + 0xE10D0 + slot × 0x24A0 + 0x2480` |
| Sluneční soustava | ukazatel `cGcSolarSystem` na `app + 0x71AF70` |
| Počet planet / aktuální index | `int32` na `solar + 0x2544` / `solar + 0x5196D0` |
| Výsledný biom / podtyp planety | `uint32` na `solar + index × 0xD9170 + 0x6148` / `+0x614C` |

Pet loader kopíruje `GcPetData+0x2B0` do runtime `+0x2480` na RVA `0x11FE63E/0x11FE644`; zapisovací cesta provádí opačnou kopii na `0x11FECBD/0x11FECC3`. Nativní vytvoření záznamu vlastního peta na `0x504A50` čte uvedený aktuální planetární biom a na `0x504B33..0x504B67` používá tento převod v pořadí: podtyp 25 → Swamp 12, podtyp 26 → Lava 13, jinak biomy 8/9/10 → Weird 7; ostatní zůstávají stejné. Mód porovnává uložený biom peta s planetou po témže převodu. Aktuální počasí, teplota ani připravenost vejce nejsou kritériem.

Čtení vyžaduje nenulový kontext a ukazatel, počet planet 1–6 a podepsaný index v rozsahu `0 <= index < count`; neplatný index se neodhaduje ani neořezává. Nativní index -1 znamená nepřítomný výběr. Konkrétní biomy jsou 0–15 mimo Test 11; All 16 a hodnoty mimo rozsah jsou neznámé. Nula je platný Lush. Podtyp musí být 0–31 a surový biom se ověří před převodem. Prázdné sloty se nečtou. Zachycené `OSError`/`ValueError` jsou omezené na volitelné čtení biomu a neoslabují pojistky nativního vyvolání. Tyto kontroly nejsou obecnou zárukou čitelnosti libovolné nenulové adresy.

Finální zdroj 0.4.1 prošel **211/211 testy**, bez chyb či přeskočených případů: 121 runtime, 34 policy, 24 settings, 14 persistence, 18 launcher. Zdroj se během běhu nezměnil; důkaz: `offline-0.4.1.json`. Se skutečným pyMHF 0.2.4 a Dear PyGui vzniklo všech osm widgetů a prošla jejich obsluha. Framework rozpoznal sedm hook callbacků pro šest cílů a nula hotkeys; hooky nebyly registrovány, viewport nebyl vytvořen a neproběhlo připojení ani nativní volání do hry. Důkaz: `framework-0.4.1.json`.

SHA256 vygenerovaného `AutoPet.py`: `234cddbc483d626cff5a637d4e4f23c912c9d5bf69b5516982b965d799164fb8`. Načtení 0.4.1 a výběr podle biomu ve hře zatím ověřené nejsou. Volitelný čtecí snímek hodnot nešlo v 13:59 pořídit, protože NMS neběžel; jde o nedostupné ověření, nikoli neúspěšný herní test.

## Co zbývá

Nevyřešené scénáře z 0.4.1 je potřeba ověřit i na přejmenované 0.4.2, včetně nového spouštěče, názvu panelu a obnovení dosavadních preferencí. Zbývá samotné načtení ve hře a preference biomu: známá shoda, žádná shoda, vypnutí, vynechání na stanici/Nexusu a zachování ručního favorita. Dosud není herně ověřena úplná sada nynějších osmi prvků panelu, preference jednotlivých lokací, opakované náhodné výběry, návrat k ručnímu favoritovi po přepnutí, zachování či migrace nastavení při restartu ani čekání bez expirace a opakování odmítnutého požadavku. Volba Random a jeden planetární výstup uspěly ve 0.4.0. Uživatel poblíž nemá vhodné místo pro zkoušku odmítnutého umístění, takže tento scénář zatím nebyl proveden a nejde o selhání. Až se přirozeně naskytne platforma archivu nebo nevhodný terén, lze zůstat déle než 12 sekund a potom bez dalšího vstupu do lodi přejít na místo, které hra dovolí. Tato zkouška má ověřit jedno vyvolání, zachování stejné volby při odmítnutí a účinnost všech způsobů zrušení.

Herně neověřené zůstává také vyvolání v Nexusu, zobrazení HUD potvrzení, přepínání OFF/ON a jeho persistence, odmítnutí na freighteru, všechny nativní větve včetně různých vstupních režimů, reakce při rychlém návratu do lodi, specifické druhy petů, dlouhodobý souběh s Companion Behavior Adjustments ani multiplayer. Statická analýza a simulované testy tyto body nenahrazují. Proto je verze stále označena jako experimentální.

Základní herní test proběhl po ukončení předchozí relace a nové záloze. Úspěch dovoluje pokračovat navazujícími testy; nepotvrzuje obecnou kompatibilitu ani připravenost pro všechny způsoby hraní.

## Primární zdroje

- [NMS.py — typy a podpisy funkcí, commit b41bf9e](https://github.com/monkeyman192/NMS.py/blob/b41bf9e6fdff1c833b77d805bb0c8da555c4ced4/nmspy/data/types.py)
- [pyMHF 0.2.4 — hooky a volání nativních funkcí](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/hooking.py)
- [pyMHF 0.2.4 — mod loader](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/pymhf/core/mod_loader.py)
- [pyMHF — samostatné skripty](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/single_file_mods.rst)
- [pyMHF — ovládací prvky GUI](https://github.com/monkeyman192/pyMHF/blob/0c8ebc1c29074c5bc35207e0aff36d4035e20bac/docs/docs/gui/gui.rst)
- [MBINCompiler — audio události](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcAudioWwiseEvents.cs)
- [MBINCompiler 7.04 pre1 — QuickMenuActions](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcQuickMenuActions.cs)
- [MBINCompiler 7.04 pre1 — společná data a SaveUniversalId](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcPlayerCommonStateData.cs)
- [MBINCompiler 7.04 pre1 — GcPetData](https://github.com/monkeyman192/MBINCompiler/blob/44f03dd1c424d64984db4b8106673bd82d2c2816/libMBIN/Source/NMS/GameComponents/GcPetData.cs)

Podrobné pracovní výpisy jsou v původní složce chatu `work/auto-pet-research`, `work/auto-pet-runtime-audit` a `work/pet-autosummon-research`. Součástí balíčku nejsou žádné herní binárky ani výpisy jejich strojového kódu.
