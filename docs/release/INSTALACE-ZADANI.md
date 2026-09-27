# Companion Auto Summon — jednoduchá a spolehlivá instalace

Požadavek vlastníka, 27. 9. 2026. Toto je zadání veřejného balíčku, nikoli popis již hotového installeru. Přejmenovaný zdrojový kandidát 0.4.2 používá Start-CompanionAutoSummon.ps1.

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
| Druhý počítač se shodnou hrou | Instalace podle krátkého návodu bez vývojových nástrojů |

Nejdříve ověřit importy a kontrolní režim mimo hru. Potom při zavřené hře po nové záloze otestovat stejný herní scénář přes nový launcher. Úspěch současného vývojového spouštěče se na nové balení automaticky nepřenáší.
