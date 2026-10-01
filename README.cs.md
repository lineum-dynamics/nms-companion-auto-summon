# Companion Auto Summon for No Man's Sky

Český překlad uživatelského návodu. Autoritativní anglická verze: [README.md](README.md).

by **Lineum Dynamics**


> Poznámka k aktuální analýze 1. 10. 2026: veřejný kandidát 0.10.1-native-test se nemění. Čtecí analýza přesného Cosmos 7.05 našla několik RIP-relative referencí na nativní stav teleportu, ale stále nemáme ověřený callback úspěšného dokončení teleportu. Podrobný záznam je v [teleportním výzkumu](docs/research/TELEPORT-AND-GROUPED-MENU.md).

Aktuální kandidát balíčku je **0.9.3-test**. Standardní knihovna Pythonu
je rozbalená, takže neobsahuje vnořený ZIP zakázaný Nexusem. Spouštěč má
správný název produktu, firmy a verzi; přiložené jsou i podklady k jeho sestavení.
Opravené je hledání Steamu při nepřístupném nesouvisejícím procesu. Herní část
zůstává beze změny: produkce **0.5.1**, společný mód **0.9.2-play-trial** a menu
**0.9.1-diagnostics**. Prošlo **786 vývojových testů** i kontroly přenosnosti,
runtime a integrity. Verze 0.9.3 ještě nebyla spuštěna ve hře ani schválena
skenery. Také soubor **49197** skončil v karanténě. Přesný ZIP má ve
VirusTotal **1/58** (Bkav Pro); je nutná kontrola moderátorem. Žádost nebyla odeslána. Podrobnosti: [ověření balíčku](docs/research/PORTABLE-SCAN-093.md).

Zachovaný distribuční kandidát **0.9.2-test**: produkce **0.5.1-experimental**,
společný mód **0.9.2-play-trial** a menu **0.9.1-diagnostics**. ZIP obsahuje
**Companion Auto Summon.exe** a Python 3.11.9; hráč Python neinstaluje ani nepoužívá
pip. Podporovaný cíl je Windows 10/11 x64, Steam **Cosmos 7.04 / build 25442159**,
.NET Framework 4 a Microsoft Visual C++ v14 x64. Text ve hře zůstává anglický.

Spouštěč před běžným startem vytváří ověřenou soukromou zálohu a používá vlastní
pracovní kopii, aby zachoval rozbalený balíček a dosavadní nastavení. Dne
28. září přibalený proces na pozadí dokončil ověřenou zálohu 49 souborů a ve
hře načetl oba módy i dvanáct hooků. Grafické okno spouštěče nebylo otevřené
ani vyzkoušené klikáním. Objevení peta, ukončení a restart, zavření okna,
druhý počítač a multiplayer **nejsou ověřené**. Podrobnosti uvádí
[LIVE-092](docs/research/LIVE-092.md).
Diagnostika známou chybu zastavení menu `unexpected_thread` neopravuje.
ZIP je sestavený a finálních **770 vývojových testů prošlo**. Kontrola
přemístěného balíčku i spouštěče prošla bez spuštění hry. Verze 0.9.2 je
na Nexusu uložená jako soubor **49196**, ale stažení blokuje automatická
karanténa. Podrobnosti eviduje [předávací záznam](docs/release/TESTER-HANDOFF.md).

Postup je v [českém rychlém návodu](docs/release/PORTABLE-QUICKSTART.cs.md).
Autor stáhne ověřený ZIP z neveřejné stránky Nexusu a předá stejný nezměněný
soubor druhému testerovi. Nejde o veřejné vydání.

Zachovaný nespouštěný kandidát **0.5.1-experimental / 0.9.1-play-trial** s menu
**0.9.0-selection** potvrzuje konkrétní změněné volby a jejich výsledné hodnoty.
Společný testovací balíček díky `gui.shown = false` neotevírá ovládací okno pyMHF;
nastavení je v herním rychlém menu. Samostatný vývojový mód si panel ponechává.
Prošlo 403 produkčních a 689 vývojových testů, kontroly skutečného frameworku
i obě kontroly před spuštěním. Společný archiv má 42 ověřených souborů.
Tento kandidát nebyl spuštěn; soubory předchozí **090-r2** zůstaly po jejím
běžném ukončení před startem 0.9.2 nezměněné. Text ve hře
zůstává anglický.

V předchozí 090-r2 se v 14:30:17 objevilo `Inert menu ordering stopped
(unexpected_thread)`: ochrana po změně vlákna callbacku zastavila naše menu,
ale ponechala filtr číselných vazeb. Produkční automatika je oddělená. Příčina
změny vlákna a souvislost s hráčovou akcí nejsou potvrzené; stejné menu v 0.9.1
tento problém neopravuje. Příchod teleportem ani odstranění základny automatiku
nespouští. Hráč hlásil chybějícího peta po příchodu a zmizení po odstranění
základny, příčina zmizení ale není prokázaná. Následuje cílené ověření životního
cyklu menu; samotné zmizení peta nemůže automaticky opravňovat jeho nové vyvolání.

Zachovaný herní test **0.5.0-experimental / 0.9.0-play-trial** s menu
**0.9.0-selection** implementuje **By habitat** (podle prostředí) a **Shuffle
companions** (střídání společníků). Prošlo 396 produkčních a 683 vývojových
testů mimo hru. Finální kandidát `090-r2` se spustil 28. 9. 2026 po ověřené
záloze 46 souborů savu a dvou souborů nastavení/stavu módu. Log potvrzuje
inicializaci produkce 0.5.0, menu 0.9.0 a načtení obou módů s dvanácti hooky.
Dosavadní nastavení schématu 3 při migraci v paměti zachovalo Random a vypnuté
střídání. Hráč potvrdil viditelného náhodného peta po načtení v Anomálii a uvedl,
že se nastavení zdá být uložené. Uložení po restartu, úplné ovládání menu,
By habitat a výsledky střídání ještě nejsou ověřené; viz
[záznam tohoto testu](docs/research/LIVE-090.md).
Dříve testovaný **0.8.7 / 087-r1**
zůstává beze změny.
By habitat na planetách váží skupiny shodné/příbuzné/přijatelné 13/5/1; stanice
a Nexus používají běžný nevážený výběr vhodných vlastních petů. Nová instalace
začíná s By habitat a zapnutým střídáním. Dosavadní schémata 1/2/3 zachovají
volby a nové střídání nechají vypnuté. Herní způsobilost ani umístění se neobchází.
Podrobnosti a hranice uvádí [anglický kontrakt výběru](docs/research/HABITAT-SELECTION.md).

Zachovaný dříve testovaný balíček **0.8.7-play-trial** spojuje produkci
**0.4.9-experimental** a menu **0.8.5-branding**. Zdroj prošel **333 produkčními
a 675 vývojovými testy** bez chyb a vynechání, kontrolou skutečného frameworku
s oběma módy a šesti dočasnými preferencemi i nezapisujícími kontrolami Python
a Windows PowerShell 5.1. Oddělený finální adresář
`build/quick-menu-play-trial-087-r1` má 41 souborů; po opravě korejského překladu
u něj znovu prošly dotčené kontroly lokalizace, frameworku a obě předstartovní
kontroly. Plný název patří do prezentace mimo hru, zatímco
ve hře zůstává **Companion Auto Summon**. Názvy tříd, souborů a cesty k osobním
datům se nemění.

Kandidát zachovává rozšířenou pasivní diagnostiku vyvolání a pouhé pozorování
jazyka hry. Nezapíná překlady a neopravuje občasné selhání při načtení v Anomálii.
Dříve připravený balíček **0.8.6-r1** zůstává nedotčený; jeho testy a vstupní
kontroly nejsou výsledky ověření tohoto nového kandidáta.

Finální **0.8.7 / 087-r1** se spustil 28. 9. 2026 po běžném ukončení hry a nové
ověřené záloze 46 souborů. V 11:07:26 (Europe/Prague) se načetly oba módy
a dvanáct nativních cílů. Hráč potvrdil viditelného náhodného peta v Nexusu
**po načtení i po výstupu z lodi**. Po požadovaném ručním odvolání pak uvedl,
že se pet zřejmě znovu neobjevil; dobu čekání nemáme nezávisle změřenou.
Šlo o různé pety; dvě úspěšná vyvolání
nevysvětlují ani neprokazují opravu [staršího selhání 0.8.4](docs/research/LIVE-084.md).
První kontrola po startu potvrdila shodu všech 40 položek balíčku i nastavení
a zapamatovaného stavu. Pozorování jazyka zaznamenalo angličtinu, ale překlady
nezapíná a neověřuje bezpečnost přepnutí jazyka. Hráč potvrdil i jednu zkoušku
nativního OFF/ON: po výstupu s OFF se pet nevyvolal, samotné ON nic nevyvolalo
a až další výstup peta vyvolal. Ostatní volby, přemapování, hlášky a ikony,
opakovatelnost, režim Last selected a multiplayer stále čekají na ověření.
Podrobnosti jsou v [záznamu 0.8.7](docs/research/LIVE-087.md).

Všech 14 katalogů nyní obsahuje 63 položek: původních 46 textů menu, hlášek,
autorských údajů a kompatibility plus sedmnáct textů přenosného spouštěče.
Katalogy používá devět zpráv kompatibility i přenosný spouštěč mimo hru.
Třináct překladů zatím není jazykově zkontrolovaných; herní menu a hlášky
zůstávají anglické. Přenosný balíček je sestavený a prošel kontrolami bez
spuštění hry; hraní a úplné jazykové ověření zbývá. Rozsah uvádí
[LOCALIZATION.md](LOCALIZATION.md).

Balíček 0.8.2 po ověřené záloze 43 souborů načetl 27. 9. 2026 v 23:58:46 oba módy a 12 nativních cílů s automatikou ON. Všech 17 souborů balíčku i osobní nastavení zůstalo shodných. Vlastní DDS je připravené a jeho hash ověřený. Viditelnou ikonu, hlášky, všech šest voleb a hraní teprve ověří hráč. Prošlo 294 produkčních a 519 vývojových testů i kontroly Windows a pyMHF.

Hlavním zdrojovým projektem je [lineum-dynamics/nms-companion-auto-summon](https://github.com/lineum-dynamics/nms-companion-auto-summon), nyní soukromý repozitář. Testovací instalace a ZIP balíčky jsou jeho výstupy; další úpravy vznikají v repozitáři. Postup sestavení a ověření je v [DEVELOPMENT.md](DEVELOPMENT.md).

Dřívější kandidát **0.4.7 / 0.8.2-play-trial** doplnil spouštěč. Parametr
`-CheckOnly` ověří balíček, podporovanou hru a existující runtime i za běhu NMS;
nic nevytváří, neinstaluje ani nespouští. Běžnou přípravu a hostitele chrání
oddělené zámky relace Windows `Setup.v1` a `Host.v1`, společné i pro balíčky
v různých složkách. Jejich platnost končí zavřením posledního systémového
handlu, také při pádu procesu. Pokud nelze zjistit běžící procesy, běžná příprava
se odmítne. Nejde o dokončený přenosný instalátor ani o herní ověření.

Produkce 0.4.7 se proti 0.4.6 liší pouze údajem o verzi. V instalaci 0.8.2
zůstává menu **0.8.0-settings-trial**. Připravená 0.8.3 přidala odlišné ikony
šesti voleb a popisek `Random: prefer matching biome`; 0.8.4 toto menu nemění.
Starší balíčky 0.7.1, 0.7.2 a 0.8.0 zůstávají nedotčené.

Zachovaný kandidát **0.4.9** a společný balíček **0.8.7-play-trial**
ukládají ručního favorita pouze po odpovídající úspěšné akci nativního ovládání
petů. Samotné přijetí požadavku do fronty, například při obnovení řízeném hrou,
favorita nezmění a nevytvoří potvrzení ruční volby. Původ konkrétního volání
po aréně není doložený; dosavadní uložený výběr proto automaticky nevracíme zpět.

Krátká potvrzení explicitních změn mají **5,5 sekundy**. Společný kandidát
přidává vlastní tlapku s kruhovou šipkou pro menu i hlášky. Pokud její textura
není připravená, použije ověřenou herní tlapku; bez použitelné ikony se celý
blok ikony skryje a zůstane text. Načtení obrázku, zmizení bílého kruhu
a čitelnost ještě vyžadují herní vizuální zkoušku.

Zachované menu 0.8.7 obsahuje šest voleb: zapnutí automatiky, poslední ruční nebo náhodný
výběr, přednost stejného biomu a samostatné povolení planet, stanic a Anomálie.
Používá dosavadní ukládání nastavení a přenastavené nativní ovládání. Textura
se připravuje při spuštění se zavřenou hrou; neznámý existující soubor
se nepřepisuje. Dočasný panel zůstává k porovnání při tomto společném testu.

Kandidát 0.8.2 byl spuštěn. Předchozí instalace **0.4.4 / 0.7.1** a připravený
starší balíček **0.4.5 / 0.7.2** zůstávají beze změny. Samostatný produkční ZIP
kandidáta 0.5.1 nemá nativní menu ani DDS; bez poskytovatele ikony používá čistý
text. Přesný rozsah kontrol aktuálního kandidáta uvádí
[technický záznam](TECHNICAL-VERIFICATION.md). Starší počty níže patří uvedeným verzím.

Historická 0.4.4 / 0.7.1 prošla 253 produkčními a 408 vývojovými testy a po
nové ověřené záloze se spustila 27. 9. 2026 v 22:22:35. Diagnostika i hráč
potvrdili jedno vyvolání v Random po načtení v Anomálii. Jeden úspěch neřeší
předchozí občasné selhání. Pasivní sledování nic znovu nevyvolává a neupravuje savy.

Pravidla vývoje a architektura jsou v anglickém [DEVELOPMENT.md](DEVELOPMENT.md). Zdrojový kód, komentáře a vývojová diagnostika jsou anglicky. Panel i herní potvrzení jsou zatím pouze anglické. Jazykové katalogy a kontrola jejich aktuálnosti už existují; zapojení do hry a jazykové i vizuální ověření zbývá. Rozsah popisuje [LOCALIZATION.md](LOCALIZATION.md).

Verze 0.4.3 přidává jednu příležitost k automatickému vyvolání po úspěšném načtení lokálního savu. Po přihlášení rovnou pěšky tedy nemusíš nejprve nastoupit a vystoupit z lodi. Mód počká na povolenou lokaci, ověření vlastnictví a původní kontroly umístění. Během samotného načítání dat žádné nativní vyvolání nevolá.

Starší vývojový balíček **0.7.0-play-trial** přidal první skutečnou volbu
v menu X: zapnutí nebo vypnutí automatiky. Změnu předává původnímu runtime
0.4.3 a jeho ukládání nastavení. Základní ON/OFF má dílčí potvrzení hráče i logu;
úplná zkouška ovládání a navigace ještě není dokončená.
Ostatní volby v této starší verzi zůstaly v dočasném panelu pyMHF; kandidát
0.8.0 je přesouvá do nativního menu. Po nové ověřené záloze byl
27. 9. 2026 spuštěn oddělený balíček 0.7.0: načetly se oba módy a 11 hook cílů
s automatikou zapnutou. Ve stejné relaci se pet po načtení v Anomálii neobjevil
navzdory přijetí požadavku a nad stavovou hláškou se ukázal nežádoucí bílý kruh.
Obě chyby zůstávají otevřené.

**Ve společném testovacím balíčku 0.6.2 se pet po načtení pěšky na vesmírné stanici automaticky objevil v režimu Random.** Log potvrzuje spuštění načtením savu bez výstupu z lodi, výběr jednoho z pěti vhodných vlastních petů a přijetí požadavku přibližně po 2,69 sekundy. Uživatel potvrdil skutečné objevení. Nexus ani planeta nebyly místem tohoto testu; jejich načtení a režim poslední ruční volby po načtení ještě čekají na ověření. Později uživatel potvrdil i jedno ruční odvolání bez opětovného objevení. Mezitím cestoval; přesné místo a délka tohoto pozorování nebyly nezávisle změřeny. Přesný rozsah zaznamenává `manifest.json`.

Kandidát 0.4.3 prošel **230 testy módu** a společný balíček 0.6.2 **341 testy vývojových nástrojů**. Kontrola se skutečným pyMHF ověřila osm prvků panelu i načtení obou tříd bez připojení ke hře. Tyto kontroly nepotvrzují skutečné objevení peta po načtení.

Předchozí verze 0.4.2 zavedla schválený název **Companion Auto Summon** místo pracovního AutoPet. Zachovala herní pravidla, výchozí hodnoty i formát osobních dat. Záložka se jmenuje **CompanionAutoSummon**, protože pyMHF používá název Python třídy. Verze 0.4.2 se následně načetla společně s testem menu v balíčku 0.6.1; log potvrdil zapnutou automatiku a přijatý požadavek po výstupu z lodi na stanici. Tento záznam nepotvrzuje nové chování 0.4.3 ani skutečné zobrazení peta.

Historický kandidát 0.4.2 prošel **212 offline testy** a kontrolou skutečného pyMHF 0.2.4 / Dear PyGui 2.3.1: jedna přejmenovaná třída módu, osm prvků nastavení, sedm callbacků pro šest cílů a žádné klávesové zkratky. Hooky nebyly registrovány, hra se nepřipojovala a nevzniklo zobrazovací okno. Samostatný regresní test ověřuje zachované umístění preferencí a ruční volby po přejmenování.

Automatické vyvolání vybraného peta po výstupu z lodi tam, kde ho dovolí hra. Výběr i zapnutí/vypnutí se pamatují po restartu. Obsahuje panel nastavení a krátké potvrzení výběru.

Předchozí AutoPet 0.4.1 přidala **Prefer same biome in Random mode**, výchozí zapnutou preferenci stejného biomu. Na planetě náhodný režim nejprve vybírá z vhodných vlastních petů se stejným domovským prostředím. Když žádný neodpovídá nebo biom nelze určit, použije běžný náhodný výběr. Poslední ruční volbu, stanice ani Nexus tato preference neovlivňuje. Chování preference biomu ještě čeká na herní ověření; níže uvedené úspěchy 0.4.0 jsou historické výsledky.

Shoda prostředí používá stejné kategorie jako hra, včetně bažinatých, lávových a exotických variant; aktuální počasí se nebere v úvahu. Mění pouze skupinu pro náhodný výběr. Jakmile je pet vybraný, přechod do jiného prostředí ho během téhož výstupu nepřelosuje.

Historický základ AutoPet 0.4.1 prošel **211 offline testy** a kontrolou vytvoření i obsluhy všech **osmi prvků nastavení** se skutečným pyMHF 0.2.4 a Dear PyGui. Kontroly proběhly bez připojení ke hře, registrace hooků a zobrazovacího okna. Načtení 0.4.1 v NMS ani výběr podle biomu ještě nejsou herně ověřené.

Verze 0.4.0 přidává samostatné volby planet, vesmírných stanic a Nexusu, režim náhodného vlastního peta a čekání na vhodné místo bez časového limitu. Výchozí nastavení: automatika zapnutá, všechny tři lokace zapnuté, poslední ručně vybraný pet. Jedno základní vyvolání v náhodném režimu na planetě už je ověřené; preference lokací a odložené vyvolání ještě čekají na herní zkoušku.

**Verze 0.4.0 úspěšně použila volbu Random a vyvolala náhodně vybraného vlastního peta na planetě.** Log z 27. září 2026 zachytil změnu nastavení, výběr slotu 3 ze tří vhodných vlastních petů a přijatý požadavek 2,86 sekundy po výstupu z lodi. Uživatel potvrdil skutečné objevení peta. Jde o jeden úspěšný výběr a vyvolání; neověřuje opakované losování, rozložení výsledků, všech sedm prvků panelu, zachování nastavení po restartu ani návrat k ručnímu favoritovi po přepnutí režimu.

Čtecí snímek runtime po náhodném vyvolání potvrdil zachovaného ručního favorita ve slotu 1, zatímco aktivní byl slot 3. To ověřuje zachování v běžící relaci, nikoli na disku nebo po restartu. Stejná relace se úspěšně načetla v 13:18:11 po nové ověřené záloze všech 42 souborů profilu, se zapnutou automatikou a jedním módem se šesti hooky. Úspěšných 197 offline testů je samostatný podklad.

**Ve verzi 0.3.3 je herně ověřené automatické vyvolání na stanici i obnovení výběru po restartu.** Test na stejném savu obnovil uloženého peta a po výstupu z lodi na stanici předal jeden požadavek; uživatel potvrdil skutečné objevení bez nového ručního výběru. Verze odstraňuje naše nadbytečné omezení pouze na planetu a připouští také Nexus v Anomálii. Vždy následují původní kontroly hry včetně místa pro vyvolání. Nexus zatím otestovaný není.

Předchozí **verze 0.3.2** ověřila základní automatické vyvolání na planetě i obnovení výběru po restartu pomocí logu a uživatelského potvrzení. Jde o dílčí úspěchy ve dvou vyzkoušených scénářích. Verze zůstává experimentální: Nexus, multiplayer, vyloučené lokace, nevhodný terén, ovládání/HUD a dlouhodobá stabilita ještě vyžadují herní ověření.

První automatické vyvolání ve verzi 0.3.1 selhalo vypršením čekání. Verze 0.3.2 doplnila nativní přepočet umístění při zavřeném menu a omezenou diagnostiku; opravený základní průchod už uvedeným testem prošel. Podklady a hranice ověření jsou v [technickém záznamu](TECHNICAL-VERIFICATION.md).

## Ovládání

Kandidát **0.9.3-test** nabízí sedm voleb přes **Quick Menu → Companions →
Companion Auto Summon**, před konkrétními pety. Na PC je výchozí klávesa **X**;
pokud sis ji změnil, použij své nastavené ovládání. V tomto balíčku se externí
panel neotevírá. Jen samostatný vývojový skript bez nativního menu ponechává
okno **pyMHF** a záložku **CompanionAutoSummon** přes **Alt+Tab**.

Sedm nativních voleb:

- **Automatic summoning**: zapne nebo vypne automatiku po načtení savu i po výstupu z lodi. Výchozí stav je ON.
- **Selection**: **Last selected**, **Random** nebo **By habitat**. Nová instalace používá By habitat; původní nastavení zůstává zachované. Každý režim respektuje vlastnictví, způsobilost a umístění podle hry.
- **Random: prefer matching biome**: výchozí ON. V Random na planetě upřednostní shodné domovské prostředí mezi vhodnými pety. OFF, neznámý biom nebo chybějící vhodná shoda znamená běžný náhodný výběr. Ostatní režimy ani herní způsobilost petů tato volba nemění.
- **Planets**: dovolí automatiku na planetách, výchozí ON.
- **Space stations**: dovolí automatiku na vesmírných stanicích, výchozí ON.
- **Space Anomaly**: dovolí automatiku v Nexusu, výchozí ON.
- **Shuffle companions**: střídá vhodné pety v Random nebo uvnitř skupiny vybrané režimem By habitat. U nové instalace je ON, po migraci starších předvoleb OFF; Last selected neovlivňuje.

Vypnutí všech tří míst zabrání automatickému vyvolání všude. Samostatný vývojový
panel má navíc údaje **Status** a **Companion**: čekající změny, hledání vhodného
místa, stav ukládání a zapamatovanou nebo aktivní volbu.

Změna se provede a uloží při další aktualizaci lokálního hráče. Hláška ukáže
výslednou hodnotu, například `Selection: By habitat` nebo `Space stations: OFF`.
Více současných změn vypíše společně; neúspěšné uložení doplní `(session only)`.
Nezměněná hodnota nevytváří potvrzení. Ze samostatného vývojového panelu se
před ukončením vrať do hry. Změna nastavení zruší čekající automatické vyvolání a ponechá již přítomného peta. Zapnutí nebo změna režimu samo nic nevyvolá — automatika počká na další výstup z lodi nebo nové načtení savu. Mód nezavádí vlastní klávesovou zkratku.

V režimu poslední ruční volby nemá nový hráč žádného předvybraného peta. Úspěšně ručně vyvolej vlastního společníka. Změněná volba požádá hru o tiché potvrzení na 5,5 sekundy: **Companion saved.** Bez úspěšného trvalého uložení uvede **Companion selected (session only).** Podle stavu doplní, že automatika je OFF nebo zůstává aktivní Random či výběr podle prostředí. Opakování stejné volby, automatické vyvolání a obnovení řízené hrou zůstávají tiché. Nové znění a zobrazení ikony nebo čistého textu ještě čekají na herní vizuální zkoušku. Hlášky a panel jsou zatím pouze anglické.

Random ani By habitat nepotřebují předchozí ruční volbu, ale vyžadují vhodného vlastního peta; ručního favorita nepřepisují. By habitat nejprve losuje skupinu shodného/příbuzného/přijatelného prostředí s váhami 13/5/1 nezávisle na počtu petů ve skupině. Jde o výslovnou návrhovou tabulku módu. Neznámý biom čeká; pokud ve známém úplném seznamu vlastních petů není žádná přípustná skupina, příležitost přeskočí s jednou hláškou. Dočasná herní nezpůsobilost čeká. Pořadí střídání spotřebuje až přijatý požadavek. Bez střídání nebo s jediným vhodným petem se může volba opakovat.

## Chování

Po úspěšném načtení lokálního savu nebo výstupu z lodi mód počká na 1,5 sekundy souvislého pobytu v zapnuté a přípustné lokaci: planeta pěšky, vesmírná stanice nebo Nexus v Anomálii. Pokud už není žádný pet aktivní ani čekající a hra dovolí peta i jeho umístění, požádá o vyvolání. Režim poslední ruční volby vyžaduje dříve vybraného vlastního peta; náhodný režim předchozí ruční volbu nepotřebuje. Ruční vyvolání jiného peta nahradí zapamatovaného favorita.

Načtení pouze zaznamená jednu příležitost. Vlastní ověření probíhá až v následných aktualizacích lokálního hráče a vlastnictví petů. Pokud uložený favorit ještě není načtený, mód ověřuje jeho úplnou identitu nejvýše dvakrát za sekundu; nepoužije náhradního peta ze stejného slotu. Chybějící první ruční volba žádného peta nevytvoří. Náhodný režim může fungovat i u savu bez trvalého ID, ale bez zapamatování volby mezi relacemi.

Na platformě archivu nebo jiném nevhodném místě čekání pokračuje bez časového limitu. Původní limit 12 sekund už neplatí. Jakmile dojdeš na vhodné místo, mód může dokončit požadavek z téhož výstupu; nemusíš znovu nastupovat do lodi. Freighter a další lokace, které nativní kontrola této verze hry nepřipouští, nadále vyvolání nedovolují. V nich mód ponechá čekání a nevolá nativní hledání místa ani vyvolání; pokračovat může až v zapnuté a přípustné lokaci. Vstup do podporované lokace, kterou jsi vypnul v nastavení Companion Auto Summon, naopak čekající výstup zruší.

Návrat do lodi, ruční náhled peta nebo související emote, ruční výběr peta, změna nastavení a další načítání savu či reset kontextu aplikace předchozí čekání zruší. Ukončí ho také zjištěný aktivní nebo jiný čekající pet. Jen úspěšné dokončení dalšího lokálního načtení může vytvořit novou příležitost; načítání cizího hráče v multiplayeru ji nevytváří. Po přijatém vyvolání mód během chůze nevrací ručně odvolaného peta až do dalšího výstupu z lodi nebo dalšího načtení savu.

Ověření vyvolání používá nativní hledání umístění včetně běžného herního dosahu. Mód připravuje místo i při zavřeném menu; neoznačuje nevhodné místo za platné. Kontroly tvoří čerstvé dvojice herních aktualizací s odstupem nejméně 0,5 sekundy mezi dvojicemi. Pokud hra požadavek nepřijme, mód počká na novou kontrolu a zkusí znovu téhož vybraného peta. Přijatý požadavek daný výstup dokončí. Čekání na platformě archivu, pozdější nalezení místa a opakování odmítnutého požadavku ještě potřebují herní test.

Automatický výběr po přípravě místa rezervuje nejvýše jednoho peta. Jeho identita a slot zůstanou pevné; změna, nejednoznačnost nebo přesun čekajícího peta do jiného slotu požadavek zruší bez náhradního losu. By habitat také hlídá kontext podporované lokace a biomu; Random zachová výběr při dočasné změně místa. Mezi příležitostmi změna pořadí slotů cyklus nerestartuje. Přijetí do herní fronty spotřebuje položku střídání, odmítnutí či zrušení nikoli. Lokální načtení nebo změna aplikace vymaže dočasné cykly; síťové načtení cizího hráče ne.

Nemění růst, rychlosti, důvěru, vejce, bojové hodnoty ani kapacity. Nezvyšuje limity vyvolání, neodemyká ani nevytváří pety a neobchází nativní omezení umístění.

## Zapamatování

Původní složka `NMS-AutoPet` zůstává záměrně zachována. Nepřejmenovávat ji: ruční favorit, preference i dosavadní vývojové prostředí dále používají stejné umístění. Přejmenování módu osobní data neresetuje ani nekopíruje.

Ruční volby petů jsou v `%LOCALAPPDATA%\NMS-AutoPet\state.json`. Každý uživatel Windows má vlastní soubor a uvnitř jsou volby rozdělené podle trvalého ID savu. Zapnutí, povolená místa, režim, `prefer_same_biome` a nové `rotate_companions` ukládá sousední `settings.json` ve schématu 4 pro všechny savy uživatele. Schéma 1 výslovně zachová Last selected; schémata 2/3 zachovají dosavadní režim a biom. Všechna starší schémata přejdou s vypnutým střídáním a zachovanými ostatními volbami. Migrace proběhne jen v paměti do výslovného uložení. Pouze nová nastavení mají By habitat a střídání zapnuté. Do samotných herních savů mód nezapisuje.

Pet se poznává kombinací CreatureSeed a BirthTime. Změna pořadí slotů nevadí. V režimu poslední ruční volby mód při odstraněném petovi nebo více nerozlišitelných shodách počká na nový ruční výběr.

Základní hra a expedice uvnitř jednoho savu sdílejí jednu volbu; obnoví se jen tam, kde pet existuje. U savu s chybějícím/nulovým ID nebo nedostupným nastavením zůstává výběr jen pro aktuální hraní. Poškozený soubor nastavení se nepřepisuje.

Pokud nelze přečíst `settings.json`, automatika začne vypnutá. V nastavení módu ji lze výslovně zapnout pro aktuální relaci. Runtime chyba je samostatná pojistka; přepínač ji neobejde.

## Spuštění a použití ostatními hráči

1. Běžně ukonči NMS, rozbal celý ZIP **0.9.3-test** do nové složky a spusť
   **Companion Auto Summon.exe** dvojklikem.
2. Zvol **Check installation**. Pokud se hra nenašla, vyber instalaci Steamu
   přes **Choose game folder** a kontrolu zopakuj. Jiný herní soubor se odmítne.
3. Zvol **Start game**. Před každým běžným startem musí projít soukromá záloha
   a její ověření; chyba spuštění zastaví. Python ani pip neinstaluješ.
4. Při prvním testu nech spouštěč otevřený a neukončuj jeho procesy na pozadí.
   Zavření okna má ponechat hraní v chodu, ale ještě to není herně ověřené.

[Český rychlý návod](docs/release/PORTABLE-QUICKSTART.cs.md) obsahuje také
jednorázový požadavek Microsoft Visual C++ x64, první zkoušky a řešení chyb.
Zálohy, logy a pracovní relace jsou pod `%LOCALAPPDATA%\NMS-AutoPet\`; původní
`settings.json` a `state.json` zůstávají zachované. Kopie zálohy se porovnává
se zdrojem před kopírováním i po něm. Aktivní relaci během hraní nemaž a osobní
data ani savy neposílej druhému testerovi.

Pro hraní bez módu běžně ukonči NMS a potom jej spusť přes Steam. Odstranění
`settings.json` obnoví výchozí hodnoty; při běžné aktualizaci se nemaže. Až oba
ověříte samostatné hraní, pokračujte podle [multiplayerového plánu](docs/release/MULTIPLAYER-TEST.md).
Viditelného peta potvrzuje každý na svém počítači; samotný požadavek v logu nestačí.

Starší postup přes PowerShell a vlastní Python zůstává vývojovou cestou,
ne postupem pro hráče přenosného balíčku. Podrobnosti jsou v
[anglickém vývojovém návodu](DEVELOPMENT.md).
