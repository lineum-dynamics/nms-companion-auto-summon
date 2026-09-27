# Companion Auto Summon — příprava prvního vydání na Nexus Mods

Stav k 27. 9. 2026. Pracovní plán; mód ani stránka nebyly zveřejněné. Hlavní zdrojový projekt už je v lokálním Gitu; tento soubor se udržuje v `docs/release/`. Odkazy na dokumenty ve složce `CompanionAutoSummon/` níže označují dokumenty v kořeni repozitáře a distribučního balíčku.

## Rozsah prvního vydání

Windows x64, Steam NMS build 25442159 / Cosmos 7.04, přesný podporovaný otisk NMS.exe, pyMHF 0.2.4 a Python 3.11–3.13 x64. Další obchody a operační systémy nejsou podmínkou prvního vydání. První veřejné vydání označit jako beta s konkrétními hranicemi ověření.

Funkce pro první vydání: automatické vyvolání vlastního peta po výstupu nebo po úspěšném načtení místního savu, poslední ruční volba nebo Random, volitelná preference domovského biomu v Random, volby lokací, zachování nastavení a čekání na vhodné místo. Kandidát 0.4.3 přidává po načtení jednu odloženou příležitost: zpracuje ji až vhodný callback místního hráče se stejným zpožděním a nativními kontrolami jako po výstupu. Během deserializace se nativní vyvolání nevolá. Ruční odvolání peta nespouští opakované automatické vyvolávání. Další funkce před dokončením ověření nepřidávat. Nativní omezení hry, vlastnictví a umístění zůstávají rozhodující.

Požadavek vlastníka: instalace musí být co nejjednodušší a nejspolehlivější. Cílový postup je **rozbalit ZIP a spustit jednu aplikaci**, s vlastním otestovaným prostředím bez ručního Pythonu, pip příkazů a systémových změn. Tento distribuční spouštěč ještě není vytvořený; stávající zdrojový kandidát 0.4.3 a kombinovaný testovací balíček 0.6.2 jsou vývojové varianty. Konkrétní požadavky jsou v `INSTALACE-ZADANI.md`.

Pořadí práce: připravit a ověřit jednoduché přenosné balení souběžně s herními zkouškami kandidáta 0.4.3 v kombinovaném balíčku 0.6.2. Nejbližší zkouška ověří odložené vyvolání po načtení a pokračující souběh s menu. Test druhého počítače už musí používat finální balení pro hráče.

Další potvrzené požadavky: celý zdrojový kód, komentáře a docstringy anglicky; uživatelské překlady odděleně. Lokalizační systém pro všech 14 oficiálních jazyků rozhraní zatím není implementovaný. Je potřeba ověřit i kódování herních potvrzení, zobrazení znaků a přepínání textů panelu. Autoritativní stav a zadání jsou v `CompanionAutoSummon/LOCALIZATION.md`; pravidla průběžné aktualizace dokumentace v `CompanionAutoSummon/DEVELOPMENT.md`.

Uživatel dále požaduje přirozené začlenění do původního rozhraní hry: nenápadná herní potvrzení a nastavení v menu X. Směr popisuje `CompanionAutoSummon/DESIGN.md`. Samostatný experiment už vkládá nativní položku a jednu neaktivní podstránku Settings preview; kombinovaný kandidát 0.6.2 ponechává menu modul 0.6.0 beze změny. Podstránka zatím nemění preference. Skutečné nastavení zůstává v panelu pyMHF, který nelze označovat za nativní herní menu. Ověření životního cyklu, zkratek, přemapování a ovladače pokračuje odděleně od připraveného vstupu do podstránky; finální herní testy se zopakují nad výsledným balíčkem.

## Doložený výchozí stav

- Stav k 27. 9. 2026: produkční kandidát 0.4.3 prošel 230 offline testy, z toho 140 testy runtime; vývojová sada prošla 341 testy. Kontrola skutečného produkčního GUI i kontrola kombinované složky 0.6.2 s pyMHF prošly mimo hru, bez registrace hooků. Kandidát 0.4.3 ani kombinovaný 0.6.2 zatím ve hře spuštěny nebyly. Původní cesty `NMS-AutoPet` pro osobní data a vývojové prostředí se zachovávají.
- Dříve téhož dne se produkční 0.4.2 úspěšně zaregistrovala v kombinovaném běhu 0.6.1. Log zaznamenal přijatý požadavek na vyvolání na stanici; viditelné objevení peta hráč nepotvrdil. To dokládá registraci a požadavek, nikoli skutečný spawn ani nové chování 0.4.3.
- Historický stav před tímto během: 0.4.2 prošla 212 offline testy a kontrolou osmi widgetů ve skutečném pyMHF 0.2.4 / Dear PyGui 2.3.1. Starší AutoPet 0.4.1 prošel 211 offline testy a kontrolou osmi widgetů; jeho preference biomu nebyla herně ověřena. Nasazení 0.4.1 je historický záznam, nikoli popis nynějšího běžícího balíčku.
- Starší 0.4.0 ověřila jeden náhodný výběr a skutečné vyvolání na planetě. Starší 0.3.3 ověřila stanici a obnovení ruční volby po restartu. Tyto výsledky, uchované před zkouškou 0.6.1 dne 27. 9. 2026, neoznačovat za herní ověření 0.4.3.
- Historická záloha 43 souborů profilu vznikla před nasazením 0.4.1. Není dokladem aktuální zálohy; před dalším testovacím spuštěním ověřit současný postup a zálohu při zavřené hře.
- Historický Git balíček 0.4.1 měl 21 souborů. Přesný seznam a kontrolní součty nového kandidáta 0.4.3 i kombinovaného 0.6.2 musí odpovídat jejich vlastním manifestům; savy, nastavení uživatele, runtime, herní binárky ani osobní logy se do vývojového ZIPu nepřibalují.

## 1. Herní test 0.4.3 v kombinovaném kandidátu 0.6.2

Vést stručný záznam verze, situace, pozorování hráče a odpovídajícího logu. Přijatý požadavek v logu sám nedokládá, že se pet skutečně objevil.

| Pokus | Očekávaný výsledek |
|---|---|
| Načtení místního savu na přípustném místě bez výstupu z lodi | Jedna odložená příležitost použije dosavadní nastavení, stejné zpoždění a nativní kontroly; nejvýše jeden vlastní způsobilý pet |
| Další běžný výstup na planetě | Dosavadní cesta vyvolání po výstupu zůstane funkční |
| Ruční odvolání po dokončení požadavku z načtení | Pet se bez nové události opakovaně nevyvolává |
| Již aktivní pet při načtení nebo nepatřičný/síťový load | Nevznikne duplicitní ani cizí automatické vyvolání |
| Známý vhodný pet stejného biomu a zapnutá preference | Výběr je ze shodných způsobilých petů; doložit skutečný domovský biom, nestačí vzhled peta |
| Bez vhodné shody biomu | Proběhne běžný náhodný výběr |
| Preference biomu OFF | Běžný náhodný výběr; jediný výstup nemusí prokázat náhodné rozložení |
| Návrat na Last manually selected | Použije se původní ruční favorit, nikoli poslední náhodný výběr |
| Vypnutí automatiky nebo konkrétní lokace | Načtení ani další výstup nespustí zakázané automatické vyvolání; již vyvolaný pet se násilně neodvolá |
| Běžné ukončení a restart přes Companion Auto Summon | Nastavení a ruční favorit se zachovají |
| Stanice a Nexus | Vyvolání závisí na původních kontrolách hry; biom nemá ovlivnit výběr |
| Nevhodné místo, vyčkání přes 20 sekund, přesun na vhodný terén | Tentýž výstup se dokončí až na přípustném místě, bez dalšího nastupování |
| Nastoupení nebo ruční volba během čekání | Starý požadavek se zruší |
| Freighter / nativně nepřípustná lokace | Žádné vyvolání obcházející pravidla hry |

Uživatel aktuálně nemá vhodné místo pro test archivu. Nejde o neúspěch; provést při dostupné příležitosti nebo se zapojením testera. Do té doby neuvádět odložené vyvolání jako herně ověřené. HUD a panel ověřit během těchto pokusů bez samostatného dlouhého testovacího běhu.

## 2. Druhý hráč a multiplayer

Nejdříve zkusit čistou instalaci distribučního balíčku na druhém Windows počítači se stejným podporovaným EXE, vlastním účtem a vlastním savem. Zkontrolovat návod, detekci Steamu, přípravu prostředí a spuštění. Nová instalace nesmí obsahovat předvoleného cizího peta.

Poté krátký společný herní test: jeden hráč s Companion Auto Summon a druhý nejprve bez něj; pozorování obou hráčů, běžný výstup, ruční odvolání a znovuvstup do lodi. Pokud bude možné, zopakovat se dvěma instancemi módu. Ověřit viditelnost peta, absenci duplicit a to, že se nemění cizí pet ani ruční volby druhého hráče. Neslibovat univerzální kompatibilitu se všemi mody nebo dlouhodobou stabilitu na základě jedné relace.

Jestli tester není dostupný, lze později připravit omezenou veřejnou betu s jasným označením neověřeného multiplayeru. Doporučený první release však zahrnuje tento test, protože multiplayer je hlavní způsob hraní vlastníka projektu.

## 3. Dokončení distribučního balíčku

- Zavést lokalizační systém, doplnit překlady a ověřit jejich obsah i zobrazení podle `LOCALIZATION.md`. Samotná existence přeložených souborů není důkaz správného překladu nebo vykreslení.
- Při sjednocení oznámení opravit také existující větev `manual favorite saved`: při chybě persistence nyní může mluvit o uložení, přestože volba platí jen pro relaci. Text musí odpovídat skutečnému výsledku; tuto okrajovou větev dosavadní herní pozorování neověřilo.
- Opravit případné chyby a zopakovat dotčené testy. Jakákoli změna nativních adres nebo herního chování vyžaduje odpovídající nový herní test; nepřenášet úspěšné výsledky automaticky na nový kód.
- Připravit veřejný spouštěč s přibaleným samostatným Python prostředím a pevně určenými verzemi závislostí. Cílem je rozbalení ZIPu a jedno kliknutí bez stahování závislostí při použití. Nejde o kopii vývojového venv; přenositelnost, načtení DLL a licence všech přibalených částí se musí ověřit. Automatické schválení takového balíčku Nexusem nelze předpokládat. Ruční instalace Pythonu je pouze současný vývojový postup, nikoli cílová instalace pro hráče.
- Doplnit autorství, kredity a rozhodnutí vlastníka o licenci / oprávnění k úpravám a redistribuci. Samostatný soubor LICENSE je vhodný způsob vyjádření, není zde označován za univerzálně povinný formát Nexusu. Cizí závislosti mají vlastní licence; automaticky na ně neuplatňovat naši licenci.
- Zkrátit uživatelský návod. Při přesunu do Gitu už byly nefunkční odkazy do soukromé testovací složky nahrazeny názvy externě uchovaných záznamů; technický dokument zachovává shrnutí výsledků. Soukromé zálohy a logy nepřibalovat.
- Aktualizovat verzi, manifest a pouze skutečně doložené výsledky; ZIP zpětně rozbalit a porovnat s manifestem.
- Připravit krátký postup instalace, aktualizace, běžného spuštění a úplného vypnutí. Uvést, že nejde o soubor pro GAMEDATA/MODS.

## 4. Stránka Nexusu

Schválený finální název: **Companion Auto Summon**. Slug repozitáře: `nms-companion-auto-summon`. Anglický návrh je v sousedním souboru `NEXUS-DESCRIPTION-DRAFT.md`. Před zveřejněním upravit instalační část podle finálního balíčku a aktualizovat testovací stav.

Přidat skutečný screenshot nastavení a ukázku výstupu z lodi / příchodu peta. Obrázky nesmějí vytvářet dojem neexistujících funkcí. Připravit požadavky, podporovaný build, seznam omezení a stručné poznámky k verzi.

Ověřená pravidla Nexusu:

- Pro převážně AI vytvořený kód použít **AI-Generated Content**; AI vytvořený veřejný popis spadá také pod **AI Media**.
- Síťové stahování má omezenou výjimku pro nezbytnou funkčnost. Pravidla neznamenají automatické schválení našeho launcheru.
- Vyplnit oprávnění k dalšímu použití a uvést použité zdroje / autory.

Zdroj: [File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines), ověřeno 27. 9. 2026.

Mód navrhnout zdarma; Donation Points zapnout při splnění podmínek. Dobrovolný odkaz na podporu přidat pouze po dodání skutečného účtu vlastníkem, bez placených funkcí či přednostního přístupu. [Donation Options & Guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines).

## 5. Zveřejnění

Před zveřejněním musí být určen účet autora, hotový funkční soubor pro vyznačený rozsah podpory, finální popis a oprávnění. Teprve potom upload a kontrola veřejné stránky i staženého ZIPu. Současný plán ani textový návrh nepotvrzují schválení Nexusem.

Další připravený krok: po běžném ukončení dosavadní hry a ověření aktuální zálohy použít oddělený kandidát 0.6.2 s produkční 0.4.3. Ověřit jednu odloženou příležitost po načtení bez změny nastavení, poté dosavadní výstup z lodi a souběh s neaktivní podstránkou menu. Tento plán není záznamem provedeného nasazení. K potvrzení samotné preference biomu je nutné znát domovské biomy dostupných petů.
