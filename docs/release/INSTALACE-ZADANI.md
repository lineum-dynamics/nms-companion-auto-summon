# Companion Auto Summon — jednoduchá a spolehlivá instalace

Požadavek vlastníka, stav k 27. 9. 2026. Toto je zadání veřejného balíčku, nikoli popis již hotového installeru. Zdrojový kandidát 0.4.3 používá Start-CompanionAutoSummon.ps1; oddělený kombinovaný kandidát 0.6.2 spouští produkční automatiku a experimentální menu modul 0.6.0 společně v jednom hostiteli. Ani jedna varianta není hotovým veřejným přenosným instalátorem.

Produkční 0.4.3 přidává jednu odloženou příležitost po úspěšném načtení místního savu vedle dosavadního výstupu z lodi. Vyhodnotí ji až vhodný callback místního hráče se stejným zpožděním a původními pravidly; při deserializaci se nativní vyvolání neprovádí. Dosavadní nastavení zůstává rozhodující a není nutné je měnit. Ruční odvolání nezpůsobuje opakované vyvolávání. Vývojová podstránka Settings preview preference zatím nemění.

Současné ověření: 230 produkčních testů (140 runtime), 341 vývojových testů a kontroly skutečného produkčního GUI i kombinované složky mimo hru prošly. Následný běh 0.4.3 / 0.6.2 dne 27. 9. 2026 po čerstvé záloze zaregistroval oba moduly s automatikou zapnutou. Po načtení místního savu na stanici vybral Random jednoho z pěti způsobilých petů a nativní fronta přijala požadavek přibližně 2,69 sekundy po jeho aktivaci; nešlo o požadavek z výstupu z lodi. Hráč potvrdil skutečné objevení peta a upřesnil, že byl na stanici, nikoli v Nexusu. Ověřené je jedno vyvolání po načtení na stanici v Random, nikoli všechny lokace ani veřejný instalátor.

Později v téže nezměněné relaci hráč potvrdil jedno ruční odvolání bez opětovného objevení peta během pozorování. Přesná lokace, čas odvolání, délka pozorování ani souvislost s dřívějším petem vyvolaným při načtení nejsou nezávisle doložené. Tento výsledek proto není označený jako odvolání na stanici nebo bezprostředně po načtení. Načtení na planetě, v Nexusu, v Last manually selected a širší regresní zkoušky zůstávají otevřené.

Historický běh 0.4.2 / 0.6.1 téhož dne doložil pouze registraci modulů a přijatý požadavek na stanici v logu, bez hráčova potvrzení spawnu. Tento starší záznam se nepřepisuje novým výsledkem.

## Nový oddělený vývojový kandidát 0.7.0

0.7.0-play-trial přidává pouze nativní zapnutí/vypnutí automatiky přes původní
frontu nastavení produkce 0.4.3. Ostatní volby a ruční favorit se zachovávají.
Stav čekající na použití a stav platný pouze pro relaci se zobrazují odlišně od
uložené volby. Prošlo 408 vývojových testů a kontrola skutečného pyMHF se dvěma
módy, 15 callbacky pro 11 cílů a dočasným nastavením mimo hru. Tato verze zatím
nebyla spuštěna; nejde o dokončený veřejný instalátor. Příprava nepřepsala
běžící 0.6.2. Nasazení vyžaduje běžné ukončení hry a čerstvou zálohu.

Finální hráčské rozhraní nebude vyžadovat panel pyMHF. Po dokončení všech voleb
v menu X se dočasný vývojový panel odstraní; závislosti GUI se posoudí zvlášť
podle frameworku. Zůstane jednoduchý spouštěč a runtime na pozadí. Nejbližší
herní zkouška ověří OFF/ON, podržení potvrzení, procházení bez změny, návrat,
znovuotevření a běžné akce petů; současné hraní může pokračovat beze změny.

## Cílový postup hráče

1. Stáhnout ZIP z Nexusu a rozbalit do vlastní zapisovatelné složky.
2. Dvojklikem otevřít aplikaci Companion Auto Summon.
3. Spouštěč ověří instalaci a nabídne **Spustit hru s Companion Auto Summon**. Pokud najde více instalací nebo Steam nelze určit, nabídne výběr složky.

Hráč nemusí instalovat Python, psát příkazy do terminálu, volit verze knihoven ani měnit systémové proměnné. Mód má mít vlastní předem otestované prostředí. Běžné spuštění nemá vyžadovat administrátorská oprávnění.

## Způsob balení k ověření

- Přenosná oficiální distribuce Pythonu pro Windows x64, pevně zvolené verze pyMHF a celého řetězce závislostí, přiložené licence a kontrolní součty.
- Samostatný malý grafický spouštěč. Vlastní runtime bude součástí ZIPu; instalační síťové operace ani automatický updater nejsou součástí cílového řešení.
- Audit současného frameworku ukázal závislost na konzolové inicializaci `questionary`, nativních DLL včetně VC runtime a inicializaci standardní knihovny v cílovém procesu. Tiché grafické spuštění ani samostatnost embedded varianty proto zatím nejsou doložené. Funkční prototyp s konzolí může být mezikrokem, nikoli vydávaným tvrzením o hotovém nenápadném launcheru.
- Nekopírovat vývojové venv. Ověřit vyhledávání modulů, nativních DLL a fyzických cest při spuštění z jiné složky a účtu.
- Ponechat zdrojový kód dostupný pro kontrolu, bez zabalování herních souborů či osobního stavu.

Oficiální Python popisuje embedded distribuci jako prostředí pro přibalení k aplikaci; externí balíčky má dodat distributor aplikace. To podporuje tento směr balení, ale samo neprokazuje kompatibilitu konkrétního pyMHF: [Python on Windows — embedded distribution](https://docs.python.org/3.11/using/windows.html#the-embeddable-package).

## Kontroly a srozumitelné chyby

- Automaticky vyhledat Steam knihovny; umožnit explicitní volbu, pokud je výsledek nejednoznačný.
- Ověřit přesný podporovaný NMS.exe a integritu našeho balíčku ještě před nativním načítáním módu.
- Běžící hru neukončovat a nesnažit se připojit druhý launcher. Zobrazit stručnou instrukci, co má hráč udělat.
- Dvojklik opakovaný v krátkém čase nesmí vytvořit dvě instance módu.
- Při neshodě hry sdělit podporovanou a nalezenou verzi, pokud je spolehlivě známá; samotný dlouhý hex řetězec nepatří do hlavního chybového hlášení.
- Nabídnout otevření složky s logem. Neodesílat logy ani uživatelská data automaticky.
- Zavření běžného ovládacího okna nesmí potichu ukončit hru. Současné provázání životního cyklu pyMHF a hry vyžaduje při návrhu launcheru výslovné ošetření a test.
- Nevypínat zabezpečení Windows, antivirovou ochranu ani pravidla pro spouštění skriptů. Nelze předem slíbit absenci upozornění SmartScreen nebo schválení antivirem.

## Aktualizace a odebrání

- Nový balíček musí zachovat nastavení a ruční volby mimo svou složku. Při přejmenování na Companion Auto Summon zůstávají cesty `%LOCALAPPDATA%\NMS-AutoPet` včetně stávajícího vývojového runtime beze změny; přejmenování není migrace dat.
- Výměnu runtime neprovádět za běhu hry; zabránit smíchání souborů dvou verzí.
- Hrát bez módu lze po úplném ukončení hry běžným spuštěním přes Steam.
- Přenosné soubory odstraňovat až po ukončení hry i runtime. Reset osobních voleb je samostatný, výslovný krok; běžné odebrání nesmí upravovat herní savy.

## Přijímací testy balíčku

| Situace | Požadovaný výsledek |
|---|---|
| Čistý Windows účet bez Pythonu v PATH | Balíček použije pouze vlastní runtime |
| Rozbalení jinam, mezery a diakritika v cestě | Spuštění nebo jasná podporovaná chyba bez nesprávného načtení DLL |
| Jiná Steam knihovna / disk | Automatické nalezení nebo funkční výběr složky |
| Závislosti bez přístupu k internetu | Není potřeba pip ani stahování; dostupnost samotného Steamu se posuzuje odděleně |
| Nesprávný herní EXE | Žádný hook ani pokus použít neověřené adresy |
| Neúplné rozbalení nebo poškozený soubor | Jasná chyba před startem módu |
| Již běžící NMS nebo druhý Companion Auto Summon | Nedojde k druhému připojení ani ukončení hry |
| Zavření okna launcheru během hry | Žádné nečekané ukončení NMS |
| Běžné ukončení NMS | Korektní ukončení doprovodného procesu |
| Nová verze balíčku | Zachované preference, bez změny herních savů |
| Načtení místního savu v 0.4.3, poté ruční odvolání | Jedna způsobilá odložená příležitost podle uložených preferencí; žádné opakované vyvolání po odvolání |
| Druhý počítač se shodnou hrou | Instalace podle krátkého návodu bez vývojových nástrojů |

Nejdříve ověřit importy a kontrolní režim mimo hru. Kandidát 0.4.3 / 0.6.2 už má potvrzené jedno vyvolání v Random po načtení na stanici a samostatně jedno ruční odvolání bez návratu peta během pozorování. Při vhodné příležitosti doplnit načtení na planetě, v Nexusu, v Last manually selected a ostatní scénáře; okamžité ukončení hry není nutné. Běžící soubory zůstávají při těchto zkouškách beze změny. Budoucí veřejné balení musí scénáře zopakovat přes vlastní launcher. Úspěch současného vývojového spouštěče se na nové balení automaticky nepřenáší.
