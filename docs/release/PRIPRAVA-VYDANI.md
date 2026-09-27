# Companion Auto Summon — příprava prvního vydání na Nexus Mods

Stav k 27. 9. 2026. Pracovní plán; mód ani stránka nebyly zveřejněné. Hlavní zdrojový projekt už je v lokálním Gitu; tento soubor se udržuje v `docs/release/`. Odkazy na dokumenty ve složce `CompanionAutoSummon/` níže označují dokumenty v kořeni repozitáře a distribučního balíčku.

## Rozsah prvního vydání

Windows x64, Steam NMS build 25442159 / Cosmos 7.04, přesný podporovaný otisk NMS.exe, pyMHF 0.2.4 a Python 3.11–3.13 x64. Další obchody a operační systémy nejsou podmínkou prvního vydání. První veřejné vydání označit jako beta s konkrétními hranicemi ověření.

Funkce pro první vydání: automatické vyvolání vlastního peta po výstupu, poslední ruční volba nebo Random, volitelná preference domovského biomu v Random, volby lokací, zachování nastavení a čekání na vhodné místo. Nové funkce před dokončením ověření nepřidávat. Nativní omezení hry, vlastnictví a umístění zůstávají rozhodující.

Požadavek vlastníka: instalace musí být co nejjednodušší a nejspolehlivější. Cílový postup je **rozbalit ZIP a spustit jednu aplikaci**, s vlastním otestovaným prostředím bez ručního Pythonu, pip příkazů a systémových změn. Tento distribuční spouštěč ještě není vytvořený; stávající zdrojový kandidát 0.4.2 je vývojový testovací balíček. Konkrétní požadavky jsou v `INSTALACE-ZADANI.md`.

Pořadí práce: připravit a ověřit jednoduché přenosné balení souběžně s herními zkouškami přejmenovaného kandidáta 0.4.2. Test druhého počítače už musí používat finální balení pro hráče.

Další potvrzené požadavky: celý zdrojový kód, komentáře a docstringy anglicky; uživatelské překlady odděleně. Lokalizační systém pro všech 14 oficiálních jazyků rozhraní zatím není implementovaný. Je potřeba ověřit i kódování herních potvrzení, zobrazení znaků a přepínání textů panelu. Autoritativní stav a zadání jsou v `CompanionAutoSummon/LOCALIZATION.md`; pravidla průběžné aktualizace dokumentace v `CompanionAutoSummon/DEVELOPMENT.md`.

Uživatel dále požaduje přirozené začlenění do původního rozhraní hry: nenápadná herní potvrzení a nastavení v menu X. Směr popisuje `CompanionAutoSummon/DESIGN.md`. Vlastní položka v menu X zatím není implementovaná a její bezpečné vložení musí projít samostatným ověřením. Neoznačovat nynější panel pyMHF za nativní herní menu. Nejbližší vývojový krok proto zahrnuje ověření menu a textové cesty souběžně s návrhem přenosného spouštěče; finální herní testy se zopakují nad výsledným balíčkem.

## Doložený výchozí stav

- Nový zdrojový kandidát 0.4.2 přejmenovává projekt na Companion Auto Summon; prošel 212 offline testy a kontrolou jedné přejmenované třídy a osmi widgetů ve skutečném pyMHF 0.2.4 / Dear PyGui 2.3.1 bez registrace hooků, připojení ke hře či viewportu. Do hry ještě nasazen nebyl. Zachovává původní cesty `NMS-AutoPet` pro osobní data i vývojové prostředí.
- Starší kandidát AutoPet 0.4.1 je v trvalé testovací instalaci; v dosavadních podkladech ještě nebyl spuštěn ve hře.
- Historická verze 0.4.1 prošla 211/211 offline testy a vytvořením/obsluhou osmi widgetů ve skutečném pyMHF / Dear PyGui bez připojení ke hře.
- Starší 0.4.0 ověřila jeden náhodný výběr a skutečné vyvolání na planetě. Starší 0.3.3 ověřila stanici a obnovení ruční volby po restartu. Tyto výsledky neoznačovat za herní ověření 0.4.1 ani 0.4.2.
- Existuje ověřená záloha 43 souborů aktuálního profilu před nasazením 0.4.1. Před dalším testovacím spuštěním ověřit, zda od ní nevznikl nový postup; při pochybnosti pořídit čerstvou zálohu při zavřené hře.
- Poslední Git balíček 0.4.1 měl 21 souborů. Přesný seznam a kontrolní součty nového balíčku 0.4.2 musí odpovídat jeho manifestu; savy, nastavení uživatele, runtime, herní binárky ani osobní logy se do vývojového ZIPu nepřibalují.

## 1. Herní test přejmenované 0.4.2 na současném počítači

Vést stručný záznam verze, situace, pozorování hráče a odpovídajícího logu. Přijatý požadavek v logu sám nedokládá, že se pet skutečně objevil.

| Pokus | Očekávaný výsledek |
|---|---|
| Načtení savu, Random, běžný výstup na planetě | Mód se načte, objeví se nejvýše jeden vlastní způsobilý pet |
| Známý vhodný pet stejného biomu a zapnutá preference | Výběr je ze shodných způsobilých petů; doložit skutečný domovský biom, nestačí vzhled peta |
| Bez vhodné shody biomu | Proběhne běžný náhodný výběr |
| Preference biomu OFF | Běžný náhodný výběr; jediný výstup nemusí prokázat náhodné rozložení |
| Návrat na Last manually selected | Použije se původní ruční favorit, nikoli poslední náhodný výběr |
| Vypnutí automatiky nebo konkrétní lokace | Další výstup nespustí automatické vyvolání; již vyvolaný pet se násilně neodvolá |
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

Po dokončení přejmenování a ověření balíčku: při zavřené hře výslovně nasadit 0.4.2, ověřit potřebnou aktuální zálohu a poté běžné spuštění přes nový launcher, načtení savu a kontrolovaný výstup z lodi na planetě v Random se zapnutou preferencí biomu. K potvrzení samotné preference je nutné znát domovské biomy dostupných petů.
