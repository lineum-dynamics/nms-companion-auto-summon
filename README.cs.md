# AutoPet 0.4.1 — testovací verze

Tento Git repozitář je hlavní zdrojový projekt. Testovací instalace a ZIP balíčky jsou jeho výstupy; další úpravy vznikají v repozitáři. Postup sestavení a ověření je v [DEVELOPMENT.md](DEVELOPMENT.md).

Pravidla vývoje a architektura jsou v anglickém [DEVELOPMENT.md](DEVELOPMENT.md). Zdrojový kód, komentáře a vývojová diagnostika jsou anglicky. Panel i herní potvrzení jsou zatím pouze anglické; systém překladů dosud neexistuje. Cílové jazyky a zbývající práce popisuje [LOCALIZATION.md](LOCALIZATION.md).

Automatické vyvolání vybraného peta po výstupu z lodi tam, kde ho dovolí hra. Výběr i zapnutí/vypnutí se pamatují po restartu. Obsahuje panel nastavení a krátké potvrzení výběru.

Verze 0.4.1 přidává **Prefer same biome in Random mode**, výchozí zapnutou preferenci stejného biomu. Na planetě náhodný režim nejprve vybírá z vhodných vlastních petů se stejným domovským prostředím. Když žádný neodpovídá nebo biom nelze určit, použije běžný náhodný výběr. Poslední ruční volbu, stanice ani Nexus tato preference neovlivňuje. Nová verze ještě čeká na herní ověření; níže uvedené úspěchy 0.4.0 jsou historické výsledky.

Shoda prostředí používá stejné kategorie jako hra, včetně bažinatých, lávových a exotických variant; aktuální počasí se nebere v úvahu. Mění pouze skupinu pro náhodný výběr. Jakmile je pet vybraný, přechod do jiného prostředí ho během téhož výstupu nepřelosuje.

Verze 0.4.1 prošla **211 offline testy** a kontrolou vytvoření i obsluhy všech **osmi prvků nastavení** se skutečným pyMHF 0.2.4 a Dear PyGui. Kontroly proběhly bez připojení ke hře, registrace hooků a zobrazovacího okna. Načtení 0.4.1 v NMS ani výběr podle biomu ještě nejsou herně ověřené.

Verze 0.4.0 přidává samostatné volby planet, vesmírných stanic a Nexusu, režim náhodného vlastního peta a čekání na vhodné místo bez časového limitu. Výchozí nastavení: automatika zapnutá, všechny tři lokace zapnuté, poslední ručně vybraný pet. Jedno základní vyvolání v náhodném režimu na planetě už je ověřené; preference lokací a odložené vyvolání ještě čekají na herní zkoušku.

**Verze 0.4.0 úspěšně použila volbu Random a vyvolala náhodně vybraného vlastního peta na planetě.** Log z 27. září 2026 zachytil změnu nastavení, výběr slotu 3 ze tří vhodných vlastních petů a přijatý požadavek 2,86 sekundy po výstupu z lodi. Uživatel potvrdil skutečné objevení peta. Jde o jeden úspěšný výběr a vyvolání; neověřuje opakované losování, rozložení výsledků, všech sedm prvků panelu, zachování nastavení po restartu ani návrat k ručnímu favoritovi po přepnutí režimu.

Čtecí snímek runtime po náhodném vyvolání potvrdil zachovaného ručního favorita ve slotu 1, zatímco aktivní byl slot 3. To ověřuje zachování v běžící relaci, nikoli na disku nebo po restartu. Stejná relace se úspěšně načetla v 13:18:11 po nové ověřené záloze všech 42 souborů profilu, se zapnutou automatikou a jedním módem se šesti hooky. Úspěšných 197 offline testů je samostatný podklad.

**Ve verzi 0.3.3 je herně ověřené automatické vyvolání na stanici i obnovení výběru po restartu.** Test na stejném savu obnovil uloženého peta a po výstupu z lodi na stanici předal jeden požadavek; uživatel potvrdil skutečné objevení bez nového ručního výběru. Verze odstraňuje naše nadbytečné omezení pouze na planetu a připouští také Nexus v Anomálii. Vždy následují původní kontroly hry včetně místa pro vyvolání. Nexus zatím otestovaný není.

Předchozí **verze 0.3.2** ověřila základní automatické vyvolání na planetě i obnovení výběru po restartu pomocí logu a uživatelského potvrzení. Jde o dílčí úspěchy ve dvou vyzkoušených scénářích. Verze zůstává experimentální: Nexus, multiplayer, vyloučené lokace, nevhodný terén, ovládání/HUD a dlouhodobá stabilita ještě vyžadují herní ověření.

První automatické vyvolání ve verzi 0.3.1 selhalo vypršením čekání. Verze 0.3.2 doplnila nativní přepočet umístění při zavřeném menu a omezenou diagnostiku; opravený základní průchod už uvedeným testem prošel. Podklady a hranice ověření jsou v [technickém záznamu](TECHNICKE-OVERENI.md).

## Ovládání

Po spuštění přes AutoPet se otevře samostatné okno **pyMHF**. Přepni se do něj přes **Alt+Tab** a vyber záložku **AutoPet**. Není to položka v nativním menu NMS.

- **Automatically summon companion after ship exit**: zapne nebo vypne automatiku. Výchozí stav je zapnuto.
- Tři samostatná zaškrtávátka dovolují automatiku na planetách, vesmírných stanicích a v Nexusu. Výchozí stav všech je zapnuto. Vypnutí všech míst znamená, že se nikde automaticky nevyvolává.
- **Companion selection** nabízí **Last manually selected** a **Random**. Výchozí je poslední ruční volba. Náhodný režim vybírá pouze z vlastních petů, které dovolí nativní kontrola hry.
- **Prefer same biome in Random mode**: výchozí zapnuto. V náhodném režimu na planetě upřednostní shodné domovské prostředí mezi již vhodnými pety. Vypnutí vrátí běžný náhodný výběr; stejný výběr se použije i při neznámém biomu nebo bez shody. Preference nemění herní způsobilost petů.
- **Status**: aktuální stav včetně **Waiting for a suitable place** (čekání na vhodné místo), případně informace, že změna čeká na návrat do hry nebo platí jen pro tuto relaci.
- **Companion**: vybraný slot, uložená volba čekající na ověření vlastnictví nebo zapnutý náhodný režim. V režimu poslední ruční volby se při prázdném výběru zobrazí výzva k prvnímu ručnímu vyvolání.

Změna se provede a uloží při další aktualizaci lokálního hráče; vrať se tedy do hry před jejím ukončením. Změna nastavení zruší čekající automatické vyvolání a ponechá již přítomného peta. Zapnutí nebo změna režimu samo nic nevyvolá — automatika počká na další výstup z lodi. Mód nezavádí vlastní klávesovou zkratku.

V režimu poslední ruční volby nemá nový hráč žádného předvybraného peta. Jednou ručně vyvolej vlastního společníka. Mód při novém výběru požádá hru o třísekundové textové potvrzení **AutoPet: companion selected for automatic summon after ship exit.** Při vypnuté automatice zpráva potvrdí výběr a uvede, že automatika je OFF. V náhodném režimu potvrdí uloženého ručního favorita a připomene, že náhodný výběr zůstává zapnutý. Stejnou volbu při opakovaném vyvolání ani obnovení po restartu znovu neoznamuje. Hlášky a panel jsou v angličtině pro sdílený balíček. Volba Random už byla úspěšně použita v herní relaci; skutečné zobrazení HUD hlášek a zbývající prvky panelu ještě potřebují ověření.

Při výslovném přepnutí do náhodného režimu není předchozí ruční volba nutná. Hráč však musí vlastnit alespoň jednoho vhodného peta; mód žádného nevytváří ani neodemyká. Náhodná volba nepřepisuje oblíbeného peta zapamatovaného pro režim poslední ruční volby. Tentýž pet může být náhodně vybrán i při následujícím výstupu.

## Chování

Po výstupu z lodi mód počká na 1,5 sekundy souvislého pobytu v zapnuté a přípustné lokaci: planeta pěšky, vesmírná stanice nebo Nexus v Anomálii. Pokud už není žádný pet aktivní ani čekající a hra dovolí peta i jeho umístění, požádá o vyvolání. Režim poslední ruční volby vyžaduje dříve vybraného vlastního peta; náhodný režim předchozí ruční volbu nepotřebuje. Ruční vyvolání jiného peta nahradí zapamatovaného favorita.

Na platformě archivu nebo jiném nevhodném místě čekání pokračuje bez časového limitu. Původní limit 12 sekund už neplatí. Jakmile dojdeš na vhodné místo, mód může dokončit požadavek z téhož výstupu; nemusíš znovu nastupovat do lodi. Freighter a další lokace, které nativní kontrola této verze hry nepřipouští, nadále vyvolání nedovolují. V nich mód ponechá čekání a nevolá nativní hledání místa ani vyvolání; pokračovat může až v zapnuté a přípustné lokaci. Vstup do podporované lokace, kterou jsi vypnul v nastavení AutoPet, naopak čekající výstup zruší.

Návrat do lodi, ruční náhled peta nebo související emote, ruční výběr peta, změna nastavení a načtení savu či reset kontextu aplikace čekání zruší. Ukončí ho také již aktivní nebo jiný čekající pet. Samotné načtení savu není spouštěčem. Po přijatém vyvolání mód během chůze nevrací ručně odvolaného peta až do dalšího výstupu z lodi.

Ověření vyvolání používá nativní hledání umístění včetně běžného herního dosahu. Mód připravuje místo i při zavřeném menu; neoznačuje nevhodné místo za platné. Kontroly tvoří čerstvé dvojice herních aktualizací s odstupem nejméně 0,5 sekundy mezi dvojicemi. Pokud hra požadavek nepřijme, mód počká na novou kontrolu a zkusí znovu téhož vybraného peta. Přijatý požadavek daný výstup dokončí. Čekání na platformě archivu, pozdější nalezení místa a opakování odmítnutého požadavku ještě potřebují herní test.

V náhodném režimu se po přípravě umístění vybere nejvýše jeden kandidát pro daný výstup. Po výběru se pet během čekání nepřelosuje. Změna jeho identity, ruční volba nebo zrušení požadavku nevyvolá náhradní los. Před vlastním požadavkem se znovu ověří identita, vlastnictví a nativní způsobilost.

Nemění růst, rychlosti, důvěru, vejce, bojové hodnoty ani kapacity. Nezvyšuje limity vyvolání, neodemyká ani nevytváří pety a neobchází nativní omezení umístění.

## Zapamatování

Ruční volby petů jsou v `%LOCALAPPDATA%\NMS-AutoPet\state.json`. Každý uživatel Windows má vlastní soubor a uvnitř jsou volby rozdělené podle trvalého ID savu. Zapnutí, povolená místa, režim výběru a `prefer_same_biome` jsou v sousedním `settings.json` ve schématu 3 a platí pro všechny savy tohoto uživatele. Schémata 1 a 2 se převedou v paměti se zapnutou preferencí biomu, přičemž zachovají dosavadní volby včetně vypnuté automatiky. Schéma 3 se zapíše až při výslovném uložení nastavení; již uložená vypnutá preference biomu se sama nezapíná. Do samotných herních savů mód nezapisuje.

Pet se poznává kombinací CreatureSeed a BirthTime. Změna pořadí slotů nevadí. V režimu poslední ruční volby mód při odstraněném petovi nebo více nerozlišitelných shodách počká na nový ruční výběr.

Základní hra a expedice uvnitř jednoho savu sdílejí jednu volbu; obnoví se jen tam, kde pet existuje. U savu s chybějícím/nulovým ID nebo nedostupným nastavením zůstává výběr jen pro aktuální hraní. Poškozený soubor nastavení se nepřepisuje.

Pokud nelze přečíst `settings.json`, automatika začne vypnutá. V panelu ji lze výslovně zapnout pro aktuální relaci. Runtime chyba je samostatná pojistka; přepínač ji neobejde.

## Použití ostatními hráči

Balíček nemá pevnou osobní cestu, účet ani tvůj save. Podporovaný cíl: Windows x64, Steam build 25442159 / Cosmos 7.04, Python 3.11–3.13 x64, pyMHF 0.2.4. Jiný herní EXE se odmítne podle kontrolního součtu; nové verze hry vyžadují novou kontrolu kompatibility.

`Start-AutoPet.ps1` vyhledá Steam a připraví vlastní Python prostředí v profilu uživatele. Při prvním nastavení stáhne `pymhf[gui]==0.2.4` včetně GUI závislostí. Při běžící hře odmítne pokračovat. Volitelný parametr `-GameDirectory` musí ukazovat na instalaci používanou aktivním Steamem. Podrobnosti jsou v [anglickém návodu](README.md).

Pro diagnostiku se zapisují logy do podsložky `logs` u AutoPet.py. Interaktivní Python konzole a samostatné logovací okno jsou vypnuté; panel nastavení zůstává dostupný.

Používej `Start-AutoPet.ps1` z běžného terminálu PowerShell. Volá pomocný `Launch-AutoPet.py`, který ověřuje skutečně načtené knihovny ještě před spuštěním Python kódu uvnitř hry. Žádné soubory nainstalovaného frameworku tím neupravuje.

Před prvním herním testem ukončit současné hraní a vytvořit novou zálohu aktuálního profilu. Ověřit osm prvků panelu, přepínač OFF/ON, jednotlivé lokace, náhodný režim, preferenci biomu a potvrzení výběru. U biomu zkusit shodného vhodného peta, žádnou shodu, vypnutí, nepoužití na stanici/Nexusu a zachování ruční volby. Na platformě archivu nebo nevhodném terénu zůstat déle než 12 sekund a potom dojít na vhodné místo: pet má přijít jednou bez dalšího výstupu z lodi. Dále ověřit běžnou planetu a peta, stanici, rychlý návrat do lodi, ruční změnu, jiný save a restart. Multiplayer až po základním ověření.

Úplné vypnutí módu: hru ukončit a příště spustit běžně přes Steam. Volby lze zapomenout odstraněním pouze souboru `state.json` při vypnuté hře; odstranění `settings.json` obnoví všechny výchozí hodnoty: automatiku zapnutou, všechny tři lokace zapnuté, poslední ruční volbu a zapnutou preferenci biomu pro náhodný režim. Samotné vložení skriptu mezi EXML módy ho nezapne.
