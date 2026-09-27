# Companion Auto Summon — rozsah ověření k 27. 9. 2026

Soukromé testovací záznamy uvedené níže jménem souboru jsou uchované mimo Git repozitář a distribuční ZIP. Dokument obsahuje jejich shrnutí; osobní záznamy ani zálohy se nedistribuují.

## Jednorázové vyvolání po načtení ve verzi 0.4.3

Úspěšné načtení lokálního savu zaznamená jednu příležitost, pokud je automatika zapnutá. Během deserializace se nevolá vyvolání ani hledání místa. Následující aktualizace lokálního vlastnictví vyhodnotí povolené místo a původní nativní kontroly. Platí stejné čekání 1,5 sekundy a stejný odstup dvojic kontrol 0,5 sekundy. Nezavádí se nový hook ani neověřená paměťová adresa.

Uložený favorit se obnovuje podle úplné identity, nikoli podle starého slotu. Chybějící záznam při načítání se ověřuje nejvýše dvakrát za sekundu. Náhodný režim využívá stejný vhodný vlastněný soubor kandidátů. Příležitost ukončí již přítomný nebo čekající pet, ruční volba či náhled, nastoupení do lodi, změna nastavení nebo změna kontextu. Po přijatém vyvolání se nepřipravuje znovu při pouhé nepřítomnosti peta.

Nová 0.4.3 zatím čeká na vlastní herní test. Připravuje se v odděleném kombinovaném balíčku 0.6.2 s dosavadním menu; běžící balíček 0.6.1 zůstává beze změny. Log předchozí 0.4.2 v balíčku 0.6.1 zaznamenal zapnutou automatiku a přijatý požadavek na stanici po výstupu z lodi, což nové spuštění po načtení nepotvrzuje.

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
