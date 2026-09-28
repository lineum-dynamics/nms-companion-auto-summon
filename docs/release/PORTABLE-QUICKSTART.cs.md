# Companion Auto Summon for No Man's Sky — by Lineum Dynamics

Český překlad návodu pro testery. Autoritativní anglická verze je **README.txt**
ve stejném ZIPu; ve zdrojovém repozitáři jde o PORTABLE-QUICKSTART.md.

## Soukromý testovací balíček 0.9.2-test

Tento návod popisuje připravovaný přenosný balíček. Spouštění, návrat k běžné hře
a multiplayer ještě vyžadují zkoušku na skutečných počítačích. Nejde o stabilní vydání.

Potřebuješ Windows 10/11 x64 s podporou .NET Framework 4, knihovny
Microsoft Visual C++ v14 x64 a Steam verzi No Man's Sky, **Cosmos 7.04 / Steam build
25442159**. Spouštěč ověřuje přesný herní soubor; jiný obchod ani novější verze
hry zatím nejsou podporované. Python 3.11.9 je součástí balíčku, takže Python
neinstaluješ a nespouštíš pip.

Autor stáhne přesný **ZIP 0.9.2-test** z neveřejné stránky Nexusu a předá
stejný nezměněný soubor druhému testerovi. Stránka zůstává neveřejná.

## Instalace a spuštění

1. Běžně ukonči No Man's Sky a nech hru úplně zavřít.
2. Rozbal celý dodaný ZIP do nové složky. Soubory ponech pohromadě; nekopíruj
   je do herní složky MODS a nepřepisuj starší testovací balíček.
3. Dvakrát klikni na **Companion Auto Summon.exe** v rozbalené složce.
4. Zvol **Check installation**. Pokud se hra nenašla, přes **Choose game folder**
   vyber svou instalaci No Man's Sky ze Steamu a kontrolu zopakuj. Když kontrola
   hru odmítne nebo ohlásí chybějící požadavek, předej autorovi přesné znění;
   kontrolu neobcházej.
5. Otevři Steam a přihlas se, potom zvol **Start game**. **Check installation**
   může běžet i při vypnutém Steamu. Před běžným spuštěním spouštěč vytvoří novou
   soukromou zálohu a porovná ji se zdrojem před kopírováním i po něm. Pokud
   ověření zálohy selže, hra s módem se nespustí.
6. Při prvním testu nech spouštěč otevřený až do běžného ukončení hry.
   Neukončuj jeho procesy na pozadí. Zavření okna má ponechat hraní v chodu,
   ale toto chování ještě čeká na ověření ve hře.

Zálohy najdeš v `%LOCALAPPDATA%\NMS-AutoPet\backups\`, každou ve vlastní složce.
Nastavení i zapamatovaní společníci zůstávají na původním místě pod
`%LOCALAPPDATA%\NMS-AutoPet\`. Ověřené soubory módu se kopírují do soukromé
složky `sessions` na stejném místě. Logy spouštěče a hostitele jsou v sousední
složce `logs`, pracovní soubory frameworku v relaci. Rozbalený
balíček by se při hraní neměl měnit. Aktivní složku relace během hraní nemaž.

## První kontrola ve hře

1. Načti save, ve kterém už vlastníš společníka. Použij planetu, stanici nebo
   Anomálii, kde hra normálně dovoluje tohoto peta vyvolat.
2. Načti se pěšky bez již přítomného peta a počkej přibližně 20 sekund. Zapiš,
   zda se opravdu objevil. Pokud se načteš uvnitř lodi, vystup a ověř tuto
   událost; načtení a výstup z lodi jsou dvě různé zkoušky.
3. Otevři **Quick Menu → Companions → Companion Auto Summon**. Výchozí klávesa
   na PC je **X**; pokud sis ji změnil, použij vlastní klávesu rychlého menu.
   Je tam sedm voleb. Hláška po změně má uvést konkrétní výslednou hodnotu.
4. Peta ručně odvolej. Má zůstat odvolaný až do dalšího výstupu z lodi nebo
   úspěšného načtení lokálního savu. Potom nastup, vystup a zkus vyvolání znovu.

Nové nastavení používá **By habitat** a **Shuffle companions ON**. Dosavadní
volby zůstávají zachované. By habitat může záměrně přeskočit nevhodný seznam
vlastních petů. Pro první jednoduché porovnání zvol **Random** a povolenou
lokaci; změna nastavení sama peta nevyvolá. Last selected nejprve vyžaduje
úspěšnou ruční volbu. Již přítomného společníka automatika nenahrazuje.

## Známá omezení a návrat k běžné hře

- Naše menu se může zastavit po změně vlákna herního callbacku. Menu
  **0.9.1-diagnostics** doplňuje záznamy, tuto chybu ale neopravuje. Nahlas,
  kdy menu přestalo fungovat a co se dělo; nespojuj příčinu automaticky
  s teleportem. Produkční automatika je od menu oddělená.
- Příchod teleportem ani odstranění základny nejsou spouštěče automatiky.
  Samotné zmizení peta nevyvolá náhradu, aby zůstalo účinné ruční odvolání.
- Menu i herní hlášky jsou anglické. Ostatní jazykové katalogy jsou návrhy.
- Přenosné spouštění, všechny volby, zachování nastavení po restartu ani
  multiplayer ještě nejsou plně ověřené. Přijatý požadavek v logu není viditelný pet.

Pokud **Check installation** ohlásí chybějící Microsoft Visual C++ runtime,
jednorázově nainstaluj [oficiální balíček Visual C++ v14 x64](https://aka.ms/vc14/vc_redist.x64.exe)
a kontrolu zopakuj. Podrobnosti uvádí [návod Microsoftu](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).
Spouštěč chybějící požadavek vysvětlí a nic automaticky nestahuje.

Chceš-li hrát bez módu, běžně ukonči NMS a potom jej spusť přes Steam.
Zálohy a původní ZIP si ponech. Při chybě spuštění předej autorovi přesné znění
a příslušný log relace; neposílej save ani složku záloh. Zapiš verzi ZIPu,
Windows a hry ze Steamu a zda se pet skutečně objevil. K postupu
**Multiplayer test.txt** v tomto ZIPu přejděte, až oba zvládnete základní
zkoušky samostatně.
