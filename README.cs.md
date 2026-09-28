# Companion Auto Summon for No Man's Sky

Český překlad uživatelského návodu. Autoritativní anglická verze: [README.md](README.md).

by **Lineum Dynamics**

Zdrojový kandidát **0.5.0-experimental / 0.9.0-play-trial** s menu
**0.9.0-selection** implementuje **By habitat** (podle prostředí) a **Shuffle
companions** (střídání společníků). Prošlo 396 produkčních a 683 vývojových
testů mimo hru; kandidát ještě nebyl spuštěn. Dříve testovaný **0.8.7 / 087-r1**
zůstává beze změny.
By habitat na planetách váží skupiny shodné/příbuzné/přijatelné 13/5/1; stanice
a Nexus používají běžný nevážený výběr vhodných vlastních petů. Nová instalace
začíná s By habitat a zapnutým střídáním. Dosavadní schémata 1/2/3 zachovají
volby a nové střídání nechají vypnuté. Herní způsobilost ani umístění se neobchází.
Podrobnosti a hranice uvádí [anglický kontrakt výběru](docs/research/HABITAT-SELECTION.md).

Zachovaný běžící balíček **0.8.7-play-trial** spojuje produkci
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

Všech 14 katalogů nyní obsahuje 46 položek, včetně nových voleb výběru/střídání,
hlášek prostředí a jednoho stavového textu vývojového panelu. Plný název a autorský kredit zůstávají pokryté.
Tři zprávy spouštěče mají rozšířený název. Při spuštění se z katalogů nyní používá pouze
devět kompatibilitních zpráv; 13 překladů jsou návrhy bez jazykové revize. Menu
a herní hlášky zůstávají anglické. Úplný překlad spouštěče ani veřejný přenosný
instalátor nejsou hotové. Rozsah uvádí [LOCALIZATION.md](LOCALIZATION.md).

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

Běžící menu 0.8.7 obsahuje šest voleb: zapnutí automatiky, poslední ruční nebo náhodný
výběr, přednost stejného biomu a samostatné povolení planet, stanic a Anomálie.
Používá dosavadní ukládání nastavení a přenastavené nativní ovládání. Textura
se připravuje při spuštění se zavřenou hrou; neznámý existující soubor
se nepřepisuje. Dočasný panel zůstává k porovnání při tomto společném testu.

Kandidát 0.8.2 byl spuštěn. Předchozí instalace **0.4.4 / 0.7.1** a připravený
starší balíček **0.4.5 / 0.7.2** zůstávají beze změny. Samostatný produkční ZIP
kandidáta 0.5.0 nemá nativní menu ani DDS; bez poskytovatele ikony používá čistý
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

Samostatný produkční balíček používá okno **pyMHF**: přes **Alt+Tab** otevři
záložku **CompanionAutoSummon**. Nový zdrojový kandidát **0.9.0** navíc
nabízí sedm voleb v rychlém menu hry, v položce **Companion Auto Summon**
před konkrétními pety. Nabídku otevři svým nastaveným herním ovládáním.
Dočasný panel zůstává během ověření k dispozici.

- **Automatically summon companion**: zapne nebo vypne automatiku po načtení savu i po výstupu z lodi. Výchozí stav je zapnuto.
- Tři samostatná zaškrtávátka dovolují automatiku na planetách, vesmírných stanicích a v Nexusu. Výchozí stav všech je zapnuto. Vypnutí všech míst znamená, že se nikde automaticky nevyvolává.
- **Companion selection** nabízí **Last manually selected**, **Random** a **By habitat**. Nová instalace používá By habitat; původní nastavení zůstává zachované. Každý režim respektuje vlastnictví, způsobilost a umístění podle hry.
- **Prefer same biome in Random mode**: výchozí zapnuto. V náhodném režimu na planetě upřednostní shodné domovské prostředí mezi již vhodnými pety. Vypnutí vrátí běžný náhodný výběr; stejný výběr se použije i při neznámém biomu nebo bez shody. Preference nemění herní způsobilost petů.
- **Shuffle companions**: střídá vhodné pety v Random nebo uvnitř skupiny vybrané režimem By habitat. U nové instalace je zapnuto, po migraci vypnuto; Last selected neovlivňuje.
- **Status**: aktuální stav včetně **Waiting for a suitable place** (čekání na vhodné místo), případně informace, že změna čeká na návrat do hry nebo platí jen pro tuto relaci.
- **Companion**: vybraný slot, uložená volba čekající na ověření vlastnictví nebo zapnutý náhodný režim. V režimu poslední ruční volby se při prázdném výběru zobrazí výzva k prvnímu ručnímu vyvolání.

Změna se provede a uloží při další aktualizaci lokálního hráče; vrať se tedy do hry před jejím ukončením. Změna nastavení zruší čekající automatické vyvolání a ponechá již přítomného peta. Zapnutí nebo změna režimu samo nic nevyvolá — automatika počká na další výstup z lodi nebo nové načtení savu. Mód nezavádí vlastní klávesovou zkratku.

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

Pokud nelze přečíst `settings.json`, automatika začne vypnutá. V panelu ji lze výslovně zapnout pro aktuální relaci. Runtime chyba je samostatná pojistka; přepínač ji neobejde.

## Použití ostatními hráči

Balíček nemá pevnou osobní cestu, účet ani tvůj save. Podporovaný cíl: Windows x64, Steam build 25442159 / Cosmos 7.04, Python 3.11–3.13 x64, pyMHF 0.2.4. Jiný herní EXE se odmítne podle kontrolního součtu; nové verze hry vyžadují novou kontrolu kompatibility.

Profil `compatibility.json` se při sestavování porovnává s deklaracemi hostitele,
nativního kódu a manifestu. Hostitelé 0.8.4 ověří vybraný EXE před importem
frameworku a před každým vložením DLL znovu ověří skutečný proces podle jeho
handlu. Odmítnou také neodpovídající konfiguraci frameworku a cizí rozšíření
`pymhflib`. Neznámý, změněný nebo nečitelný EXE zabrání aktivaci módu; chyba se
zobrazí mimo hru a preference se neresetují. Tyto kontroly prošly testy mimo
hru; podporované spuštění přes kontrolovaný host prošlo také v relaci 0.8.4.
Běžící 0.8.7 má výše vymezené potvrzení; nový zdrojový kandidát 0.9.0 zatím spuštěn nebyl.

Kompatibilitní zprávy vybírají jazyk podle prostředí Windows; parametr
`-Language`, například `-Language fr`, jej může změnit. Nejde o zjištění jazyka
hry. `-NoDialog` ponechá chybu v konzoli bez dialogu; dialogy nezobrazuje ani
`-CheckOnly`. Při poškozeném překladu se použije stručná anglická chyba balíčku.
Ostatní zprávy přípravy zatím zůstávají anglické.

Pro kontrolu rozbaleného kandidáta spusť v PowerShellu
`./Start-CompanionAutoSummon.ps1 -CheckOnly`. Hra může zůstat zapnutá.
Kontrola ověří dostupné soubory balíčku, hry a runtime; chybějící požadavky
ohlásí, ale nic nevytvoří, nestáhne, nezkopíruje do hry ani nespustí.
Úspěšná kontrola neověřuje herní funkce a nenahrazuje zálohu před novým testem.

Při běžném spuštění `Start-CompanionAutoSummon.ps1` vyhledá Steam a připraví vlastní Python prostředí v profilu uživatele. Při prvním nastavení stáhne `pymhf[gui]==0.2.4` včetně GUI závislostí. Při běžící hře nebo chybě zjišťování procesů odmítne pokračovat. Ochrana proti dvojímu spuštění platí i mezi různými složkami balíčků a po skončení procesu nezanechává zámkový soubor. Volitelný parametr `-GameDirectory` musí ukazovat na instalaci používanou aktivním Steamem. Podrobnosti jsou v [anglickém návodu](README.md).

Pro diagnostiku se zapisují logy do podsložky `logs` u CompanionAutoSummon.py. Interaktivní Python konzole a samostatné logovací okno jsou vypnuté; panel nastavení zůstává dostupný.

Používej `Start-CompanionAutoSummon.ps1` z běžného terminálu PowerShell. Volá pomocný `Launch-CompanionAutoSummon.py`, který ověřuje skutečně načtené knihovny ještě před spuštěním Python kódu uvnitř hry. Žádné soubory nainstalovaného frameworku tím neupravuje.

Před prvním herním testem ukončit současné hraní a vytvořit novou zálohu aktuálního profilu. Ověřit osm prvků panelu, přepínač OFF/ON, jednotlivé lokace, náhodný režim, preferenci biomu a potvrzení výběru. U biomu zkusit shodného vhodného peta, žádnou shodu, vypnutí, nepoužití na stanici/Nexusu a zachování ruční volby. Na platformě archivu nebo nevhodném terénu zůstat déle než 12 sekund a potom dojít na vhodné místo: pet má přijít jednou bez dalšího výstupu z lodi. Dále ověřit běžnou planetu a peta, stanici, rychlý návrat do lodi, ruční změnu, jiný save a restart. Multiplayer až po základním ověření.

Úplné vypnutí módu: hru ukončit a příště spustit běžně přes Steam. Volby lze zapomenout odstraněním pouze souboru `state.json` při vypnuté hře; odstranění `settings.json` obnoví všechny výchozí hodnoty: automatiku zapnutou, všechny tři lokace zapnuté, poslední ruční volbu a zapnutou preferenci biomu pro náhodný režim. Samotné vložení skriptu mezi EXML módy ho nezapne.
