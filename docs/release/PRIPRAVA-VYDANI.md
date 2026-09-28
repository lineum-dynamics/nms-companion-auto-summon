# Companion Auto Summon — příprava prvního vydání na Nexus Mods

Stav k 28. 9. 2026. Pracovní plán; mód ani stránka nebyly veřejně zveřejněné. Hlavní zdrojový projekt je v soukromém GitHub repozitáři; tento soubor se udržuje v `docs/release/`. Odkazy na dokumenty ve složce `CompanionAutoSummon/` níže označují dokumenty v kořeni repozitáře a distribučního balíčku.

Aktuální zdroj je **0.4.8 / 0.8.6**, zatím nespuštěný. Běží neměnná **0.4.7 / 0.8.4**.
Snímky potvrzují šest odlišných ikon nastavení. Načtení v Anomálii jednou selhalo
vizuálně, pozdější výstup z lodi vyvolal jiného náhodného peta úspěšně. Příčinu
neznáme. Kandidát zachovává prodloužené pasivní sledování v původních limitech
a přidává pouze čtení jazyka pro diagnostiku při otevření našeho menu;
podrobnosti uvádí [záznam 0.8.4](../research/LIVE-084.md). Úplné ověření menu,
hlášek, přemapování, lokalizace a veřejného přenosného spouštěče stále čeká.
Monetizaci shrnuje [aktuální přehled pravidel](MONETIZATION.md).

Mimo herní balíček je nově připravené skládání přeložených textů: všech 1 666
kombinací jazyků a stavů se vejde do stávajících limitů bez zkrácení. Samotné
vykreslení a automatický výběr jazyka ještě ověřené nejsou. Také prošel skutečný
test importu pyMHF bez konzole, včetně reprodukce původní chyby a jejího vyřešení
prototypem. Současný spouštěč ho zatím nepoužívá; přenosná instalace tím není
hotová. Podrobnosti: [lokalizace](../research/NATIVE-LOCALIZATION-AUDIT.md) a
[přenosný runtime](../research/PORTABLE-RUNTIME-AUDIT.md).

## Nejbližší společný test 0.8.6

Prioritou je zachytit občasné selhání po načtení v Anomálii. Běžící 0.8.4 se
nemění a její host se neukončuje. Oddělenou 0.8.6 nasadit při příštím běžném
ukončení hry, po ověření nové zálohy a shody připraveného balíčku. Diagnostika
nemění pravidla vyvolávání a sama o sobě závadu neopravuje.

Připravený finální adresář je `build/quick-menu-play-trial-086-r1`; starší
výstup `086` je překonaný a nesmí se spouštět. Prošlo 675 vývojových testů,
kontrola skutečného frameworku mimo hru a obě nezapisující předstartovní kontroly.
Produkce 0.4.8 zůstává totožná s dříve ověřeným kandidátem (333 testů).

1. Po načtení na povoleném místě vyčkat přibližně 20 sekund bez změn nastavení,
   otevření náhledu petů nebo ručního vyvolání. Zaznamenat skutečně viditelného
   peta či jeho nepřítomnost a celý omezený diagnostický průběh.
2. Potom ve stejné relaci porovnat běžný výstup z lodi. Random může vybrat jiného
   peta; takový výsledek nerozliší příčinu v načítání od rozdílu mezi pety. Pokud
   bude potřeba řízené srovnání, použít stejného ručně zvoleného peta v režimu
   Last selected při dalším přirozeném načtení i výstupu. Neopakovat automaticky
   přijatý požadavek a nezaměňovat ruční odvolání za chybu.
3. Až po úvodním pozorování spojit ověření šesti voleb, návratu/znovuotevření
   menu, běžného ručního vyvolání a odvolání s kontrolou čitelnosti hlášek a
   jejich ikon. Ověřit zachování ostatních voleb; na konci vrátit uživatelovy
   preference. Přemapování a ovladač označit za ověřené pouze po skutečném testu.
4. Výběr položky Companion Auto Summon zároveň pořídí omezené diagnostické
   čtení jazyka. Při první zkoušce jazyk hry neměnit. Texty zůstávají anglické;
   tato verze ještě překlady nezapíná. Čtení se při chybě samo zastaví bez
   vypnutí menu nebo automatiky.

Další herní ověření vyžaduje běžné ukončení a nové spuštění hry. Přenosný
instalátor lze dál připravovat mimo běžící prostředí. Odstranění panelu pyMHF následuje po přijetí
všech nativních ovládacích prvků. Žádný z těchto kroků nepotvrzuje veřejnou
připravenost, multiplayer ani správnost dosud neotestovaných překladů.

Následující výsledky 0.4.4 / 0.7.1 a 0.7.0 jsou historický záznam; jejich
tehdejší další kroky nepopisují současně běžící verzi.

## Historická příprava a test 0.4.4 / 0.7.1

Tehdy připravovaný kandidát byl 0.4.4 v odděleném balíčku 0.7.1. Přidává
pouze pasivní sledování po přijetí požadavku. Neopakuje vyvolání, nemění
prodlevy ani preference. Po nové záloze se 27. 9. 2026 v 22:22:35
načetly oba módy a 11 hook cílů s automatikou ON; viditelný výsledek čeká. Základní přepínání
v předchozím 0.7.0 má dílčí potvrzení, ale po načtení v Anomálii se pet neobjevil
navzdory přijetí požadavku. Diagnostika má zjistit další průběh. Bílý kruh
u hlášky zůstává samostatnou chybou vzhledu. Níže jsou starší výsledky 0.4.3;
na nový kandidát se nepřenášejí. Veřejné vydání je nadále předčasné.

Jedno vyvolání v Random po načtení v Anomálii je pro 0.4.4 / 0.7.1 potvrzené. Dne 27. 9. 2026 log zaznamenal aktivaci načtením v 22:23:39.698, přijetí frontou v 22:23:42.250 (uváděných 2,56 sekundy) a očekávaného aktivního peta v 22:23:42.266 při první aktualizaci diagnostiky. Hráč potvrdil skutečné objevení. Nepředcházel výstup z lodi ani opakované vyvolání. Jde o jeden úspěšný běh; předchozí občasné selhání není tímto opravené, protože změna byla pouze diagnostická.

## Připravený test nativního nastavení 0.7.0

Oddělený balíček 0.7.0-play-trial obsahuje nezměněnou produkci 0.4.3 a první
nativní přepínač automatického vyvolávání ON/OFF. Prošlo 408 vývojových testů,
kontrola skutečného pyMHF mimo hru a zařazení/použití změny dočasného nastavení.
Balíček má 15 souborů, dva módy a 15 callbacků pro 11 cílů. Po ukončení hry
a nové ověřené záloze 43 souborů se 27. 9. 2026 v 21:48:38 zaregistrovaly
oba módy a 11 hook cílů s automatikou ON. Úplné herní ověření přepínače čeká;
pozorování z 0.6.2 níže novou nabídku neověřují.

Nejbližší zkouška v nyní běžící hře: samotné procházení
nesmí měnit stav; samostatné potvrzení má přepnout OFF/ON, podržení pouze jednou.
Ověřit návrat, znovuotevření, pořadí položek, zachování ostatních voleb a ruční
vyvolání peta. Další restart není pro tuto zkoušku potřeba. Aktivační
cesty bez ověřeného nativního potvrzení nic nepřepínají; přemapování a ovladače
je potřeba samostatně vyzkoušet. Ostatní volby zatím používají dočasný panel
pyMHF. Ten se po dokončení a ověření celého nativního menu odstraní z hráčského
rozhraní, se zachováním uložených preferencí a běhu frameworku na pozadí.

## Rozsah prvního vydání

Windows x64, Steam NMS build 25442159 / Cosmos 7.04, přesný podporovaný otisk NMS.exe, pyMHF 0.2.4 a Python 3.11–3.13 x64. Další obchody a operační systémy nejsou podmínkou prvního vydání. První veřejné vydání označit jako beta s konkrétními hranicemi ověření.

Funkce pro první vydání: automatické vyvolání vlastního peta po výstupu nebo po úspěšném načtení místního savu, poslední ruční volba nebo Random, volitelná preference domovského biomu v Random, volby lokací, zachování nastavení a čekání na vhodné místo. Kandidát 0.4.3 přidává po načtení jednu odloženou příležitost: zpracuje ji až vhodný callback místního hráče se stejným zpožděním a nativními kontrolami jako po výstupu. Během deserializace se nativní vyvolání nevolá. Ruční odvolání peta nespouští opakované automatické vyvolávání. Další funkce před dokončením ověření nepřidávat. Nativní omezení hry, vlastnictví a umístění zůstávají rozhodující.

Požadavek vlastníka: instalace musí být co nejjednodušší a nejspolehlivější. Cílový postup je **rozbalit ZIP a spustit jednu aplikaci**, s vlastním otestovaným prostředím bez ručního Pythonu, pip příkazů a systémových změn. Tento distribuční spouštěč ještě není vytvořený; stávající zdrojový kandidát 0.4.3 a kombinovaný testovací balíček 0.6.2 jsou vývojové varianty. Konkrétní požadavky jsou v `INSTALACE-ZADANI.md`.

Pořadí práce: připravit a ověřit jednoduché přenosné balení souběžně s herními zkouškami kandidáta 0.4.3 v kombinovaném balíčku 0.6.2. Potvrzené je jedno vyvolání v Random po načtení na stanici a samostatně jedno ruční odvolání bez návratu peta během pozorování. Při vhodné příležitosti doplnit načtení na planetě, v Nexusu a v režimu Last manually selected; není kvůli tomu nutné ihned ukončovat hru. Test druhého počítače už musí používat finální balení pro hráče.

Další potvrzené požadavky: celý zdrojový kód, komentáře a docstringy anglicky; uživatelské překlady odděleně. Lokalizační systém pro všech 14 oficiálních jazyků rozhraní zatím není implementovaný. Je potřeba ověřit i kódování herních potvrzení, zobrazení znaků a přepínání textů panelu. Autoritativní stav a zadání jsou v `CompanionAutoSummon/LOCALIZATION.md`; pravidla průběžné aktualizace dokumentace v `CompanionAutoSummon/DEVELOPMENT.md`.

Uživatel dále požaduje přirozené začlenění do původního rozhraní hry: nenápadná herní potvrzení a nastavení v menu X. Směr popisuje `CompanionAutoSummon/DESIGN.md`. Samostatný experiment už vkládá nativní položku a jednu neaktivní podstránku Settings preview; kombinovaný kandidát 0.6.2 ponechává menu modul 0.6.0 beze změny. Podstránka zatím nemění preference. Skutečné nastavení zůstává v panelu pyMHF, který nelze označovat za nativní herní menu. Ověření životního cyklu, zkratek, přemapování a ovladače pokračuje odděleně od připraveného vstupu do podstránky; finální herní testy se zopakují nad výsledným balíčkem.

## Doložený výchozí stav

- Stav k 27. 9. 2026: produkční kandidát 0.4.3 prošel 230 offline testy, z toho 140 testy runtime; vývojová sada prošla 341 testy. Kontrola skutečného produkčního GUI i kontrola kombinované složky 0.6.2 s pyMHF prošly mimo hru, bez registrace hooků. Původní cesty `NMS-AutoPet` pro osobní data a vývojové prostředí se zachovávají.
- Následný herní běh 0.4.3 / 0.6.2 po nové záloze 43 souborů zaregistroval ve 20:42:21 dva moduly a deset nativních hook cílů, s automatikou zapnutou. Log ve 20:42:58.578 zaznamenal požadavek po načtení místního savu, lokaci 2 (stanice), ve 20:43:01.260 náhodný slot 1 z pěti způsobilých petů a ve 20:43:01.261 přijetí požadavku do nativní fronty. Od aktivace požadavku do přijetí uplynulo přibližně 2,69 sekundy; není to měření okamžiku viditelného spawnu. Nepředcházel požadavek z výstupu z lodi. Hráč potvrdil, že se pet po načtení opravdu objevil, a upřesnil stanici, nikoli Nexus. Doložený rozsah je jedno vyvolání po načtení na stanici v Random.
- Později v téže nezměněné relaci 0.4.3 / 0.6.2 hráč potvrdil jedno ruční odvolání a to, že se pet během pozorování znovu neobjevil. Přesná lokace, čas odvolání a délka pozorování nebyly nezávisle doloženy; nelze ani spojit odvolaného peta s dřívějším vyvoláním při načtení. Jde o samostatné potvrzení hráče, nikoli o test odvolání na stanici nebo bezprostředně po načtení.
- Dříve téhož dne se produkční 0.4.2 úspěšně zaregistrovala v kombinovaném běhu 0.6.1. Log zaznamenal přijatý požadavek na vyvolání na stanici; viditelné objevení peta hráč nepotvrdil. To dokládá registraci a požadavek, nikoli skutečný spawn ani nové chování 0.4.3.
- Historický stav před tímto během: 0.4.2 prošla 212 offline testy a kontrolou osmi widgetů ve skutečném pyMHF 0.2.4 / Dear PyGui 2.3.1. Starší AutoPet 0.4.1 prošel 211 offline testy a kontrolou osmi widgetů; jeho preference biomu nebyla herně ověřena. Nasazení 0.4.1 je historický záznam, nikoli popis nynějšího běžícího balíčku.
- Starší 0.4.0 ověřila jeden náhodný výběr a skutečné vyvolání na planetě. Starší 0.3.3 ověřila stanici a obnovení ruční volby po restartu. Tyto výsledky, uchované před zkouškou 0.6.1 dne 27. 9. 2026, neoznačovat za herní ověření 0.4.3.
- Historická záloha 43 souborů profilu vznikla před nasazením 0.4.1; oddělená nová záloha 43 souborů předcházela nynějšímu běhu 0.4.3 / 0.6.2. Před dalším nasazením znovu posoudit aktuálnost zálohy podle nového herního postupu.
- Historický Git balíček 0.4.1 měl 21 souborů. Přesný seznam a kontrolní součty nového kandidáta 0.4.3 i kombinovaného 0.6.2 musí odpovídat jejich vlastním manifestům; savy, nastavení uživatele, runtime, herní binárky ani osobní logy se do vývojového ZIPu nepřibalují.

## 1. Herní test 0.4.3 v kombinovaném kandidátu 0.6.2

Vést stručný záznam verze, situace, pozorování hráče a odpovídajícího logu. Přijatý požadavek v logu sám nedokládá, že se pet skutečně objevil.

Potvrzeno v tomto kandidátu: jedno načtení na stanici v Random s viditelným petem a samostatně jedno ruční odvolání bez návratu peta během hráčova pozorování. Načtení na planetě a v Nexusu, načtení v Last manually selected, širší regrese odvolání a ostatní scénáře tabulky tím ověřeny nejsou.

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

Pravidla Nexusu pro zveřejnění a monetizaci, ověřená 28. 9. 2026:

- Pro převážně AI vytvořený kód, UI a překlady použít **AI-Generated Content**; AI vytvořený veřejný popis nebo propagační média spadají také pod **AI Media**. Samotné **AI Assisted** vyžaduje omezené zapojení AI a doloženou lidskou tvorbu i odbornou znalost; není to vhodná náhrada pro současný rozsah CAS.
- Síťové stahování má omezenou výjimku pro nezbytnou funkčnost. Pravidla neznamenají automatické schválení našeho launcheru.
- Vyplnit oprávnění k dalšímu použití a uvést použité zdroje / autory.

Zdroj: [File Submission Guidelines](https://help.nexusmods.com/article/28-file-submission-guidelines), aktualizováno 4. 9. 2026.

Cílem vlastníka je maximální příjem v mezích pravidel, nikoli předem omezená nenápadná propagace. Nexus umožňuje kombinovat podmíněné Donation Points, PayPal a externí dárcovské odkazy. Aktuální [DP pravidla](https://help.nexusmods.com/article/68-donation-points-system-terms-of-service) neobsahují plošné vyloučení AI; způsobilost závisí na právech k obsahu a rozhodnutí Nexusu. Neslibovat výdělek.

[Donation Options & Guidelines](https://help.nexusmods.com/article/77-donation-options-guidelines) povolují odkazy na stránkách Nexusu; tím není schválen finanční prvek ve hře ani launcheru. Přesná frekvence připomínek nebo rozměr dárcovského banneru není určena. Limit 100 px se týká odkazů na zvlášť schválený placený obsah, ne obecně darů. Výklad [EULA Hello Games](https://www.nomanssky.com/end-user-licence-agreement/) pro lokální finanční UI zůstává nevyjasněný. [Přehled](MONETIZATION.md) zachovává neodeslané pracovní dotazy; vlastník výslovně zakázal kontaktování obou organizací. Vycházet pouze z publikovaných pravidel.

Aktuální návrh spojuje oznámení o aktivaci s neutrální informací, kde lze
dobrovolně přispět. Je zapsaný v přehledu; četnost a cílový odkaz nejsou určeny.
Samotné spojení textů nezakládá výjimku z pravidel. Nejde o implementovanou
hlášku ani potvrzené povolení této podoby. Při zavedení skutečného textu musí
současně vzniknout odpovídající anglický záznam a všechny dotčené překlady.

## 5. Zveřejnění

Před zveřejněním musí být určen účet autora, hotový funkční soubor pro vyznačený rozsah podpory, finální popis a oprávnění. Teprve potom upload a kontrola veřejné stránky i staženého ZIPu. Současný plán ani textový návrh nepotvrzují schválení Nexusem.

Další zkoušky lze doplnit při vhodné příležitosti: načtení na planetě a v Nexusu, načtení v Last manually selected, dosavadní výstup z lodi a souběh s neaktivní podstránkou menu. Bezprostřední ukončení hry není podmínkou pokračování práce; běžící kandidát se nemění. K potvrzení samotné preference biomu je nutné znát domovské biomy dostupných petů. Jedno potvrzené odvolání nenahrazuje širší regresní zkoušky.
