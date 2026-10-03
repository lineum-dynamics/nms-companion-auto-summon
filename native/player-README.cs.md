# Companion Auto Summon for No Man's Sky - by Lineum Dynamics

**0.10.2-native-test — EARLY ALPHA pro test multiplayeru.** Windows 10/11,
64bit, Steam. Dřívější sestavení tohoto pokusného spouštěče vyvolalo viditelného
peta po dvou místních trasách teleportu. Nepotvrzuje to, kterou herní událost
spouštěč zachycuje, zda reaguje jen na místního hráče ani co udělá, když se
teleportuje jiný hráč. Tento přesný archiv ještě potřebuje nový test spuštění.
Před testem si ponechte samostatnou zálohu vytvořenou při vypnuté hře.

## Instalace

1. Vypněte No Man's Sky. Ukončete také předchozí launcher Companion Auto Summon
   nebo relaci pyMHF. Pythonová a nativní verze nesmějí běžet současně.
2. Ve Steamu klikněte pravým tlačítkem na **No Man's Sky → Spravovat →
   Procházet místní soubory**. Otevře se složka hry s `Binaries` a `GAMEDATA`.
3. ZIP rozbalte do dočasné složky. Pokud už herní `Binaries` obsahuje
   `winmm.dll`, **nepřepisujte ho**. Znovu ho lze použít jen při přesné shodě
   SHA-256 s hodnotou níže. Při jiné hodnotě instalaci zastavte: jiný mód může
   tento loader potřebovat.
4. Z rozbaleného balíčku zkopírujte složky **Binaries** a **GAMEDATA** do
   složky hry a slučte je s existujícími složkami. Při aktualizaci tohoto módu
   nahrazujte pouze jeho `CompanionAutoSummon.asi` a ikonky. Balíček neobsahuje
   spustitelný soubor hry.
5. Hru spusťte běžně přes **Steam**. Není potřeba instalovat Python, používat
   zvláštní launcher, spouštět příkaz jako správce ani otevírat panel nastavení
   mimo hru.

Do hry patří právě tyto soubory:

- `Binaries/winmm.dll` — oficiální Ultimate ASI Loader 9.7.4, x64.
- `Binaries/scripts/CompanionAutoSummon.asi` — nativní modul tohoto módu.
- Osm vlastních ikonek ve složce
  `GAMEDATA/MODS/CompanionAutoSummon/TEXTURES/UI/FRONTEND/ICONS/COMPANIONAUTOSUMMON/`.

Schválená hodnota SHA-256 loaderu:
`fa266e3513d02c08a1b808f28c10538a489eaffaa4b0707f7cc1066e71b5afd7`.
Obsah loaderu odpovídá oficiálnímu souboru `dinput8.dll`; `winmm.dll` je jeden
z podporovaných názvů tohoto loaderu. Soubor `.asi` je nativní DLL ve formátu
používaném loaderem. Oba soubory nadále podléhají antivirové kontrole. Pokud je
antivirus zablokuje, blokaci ponechte a nahlaste název detekce. Nevytvářejte
antivirovou výjimku ani nestahujte neověřenou náhradu.

## Nastavení ve hře

Otevřete **rychlé menu → Companions → Companion Auto Summon**. Výchozí klávesa
rychlého menu na PC je **X**; po změně ovládání použijte vlastní přiřazenou
klávesu nebo pokyn hry pro ovladač. Mód reaguje na herní akce menu, nikoli na
napevno zvolenou klávesu. Nastavení je před seznamem konkrétních petů.

Nová instalace má automatiku zapnutou na planetách, vesmírných stanicích a
v Anomálii. Výchozí volby jsou **By habitat** a zapnuté **Shuffle**. Existující
nastavení se zachová; aktualizace vaše dřívější volby nepřepíná na výchozí.

- **By habitat:** vybírá z vašich petů podle vhodnosti prostředí. Dostupné
  skupiny se shodným, příbuzným a přijatelným biomem mají relativní váhy 13:5:1.
  Stanice a Anomálie používají neutrální výběr. Na vulkanické planetě může být
  vhodný příbuzný scorched pet. Pokud žádný váš pet nevyhovuje, mód nevyvolá
  nevhodnou náhradu.
- **Random:** náhodně vybere peta, kterého máte a kterého hra dovolí vyvolat.
  Samostatná přednost stejného biomu se vztahuje pouze k tomuto režimu.
  Shuffle může přijaté výběry střídat.
- **Last selected:** použije posledního potvrzeného ručně vybraného peta
  pro konkrétní save. Nový hráč ho v tomto režimu musí nejprve vyvolat ručně.
- **Shuffle:** postupuje až po přijetí požadavku hrou. Dočasně nevhodné místo
  ani odmítnutí požadavku nepřelosuje peta; další pokus používá stejného.

Automatika dostane jednu příležitost po úspěšném načtení místního savu nebo
výstupu z lodi. Tato testovací verze obsahuje také experimentální callback
teleportu, který byl pozorován po dvou místních trasách. Jeho přesný význam a
chování v multiplayeru vůči místním a vzdáleným hráčům nejsou ověřené. Hlavní
přepínač automatiky a nastavení míst stále určují, zda může dojít k vyvolání.
Každý požadavek čeká na herní kontrolu vlastnictví, fyziky a místa. Z nevhodného
terénu se přesuňte na volnou zem; čekající požadavek může pokračovat, jakmile
hra vyvolání dovolí. Ruční odvolání peta nevytvoří nový požadavek. Náhled petů,
nástup do lodi, změna nastavení nebo přijaté ruční vyvolání původní požadavek
zruší. Mód nevytváří nové pety, nesnižuje herní limity, nezkracuje herní
časovače ani neobchází pravidla běžného vyvolávání.

## Multiplayerový test

Oba hráči mají nainstalovat tentýž archiv a podporovanou verzi hry pro
Windows/Steam. Nejprve ověřte, že je automatika zapnutá a současné místo
povolené. V multiplayeru jeden hráč zůstane stát a druhý se teleportuje.
Sledujte, zda se prvnímu hráči vyvolá jeho vlastní pet, a potom si role
prohoďte. Pokud je chování rušivé, vypněte automatiku v herním menu. Při
hlášení uveďte, který hráč se teleportoval, kde se oba nacházeli, zda už byl
nějaký pet aktivní, režim výběru a co se zobrazilo na každé obrazovce. Test má
zjistit, zda experimentální spouštěč reaguje i na pohyb druhého hráče.

## Kompatibilita, ukládání a zálohy

Tato testovací verze cílí pouze na **Steam Cosmos 7.05, build 25624745**,
SHA-256 `671de22649274b49fa07f5a246bc7252c4e08bb9ab623d2e65722fbab4e497a4`.
Kandidát před zapojením herních funkcí ověří skutečný spustitelný soubor. Shoda
v této kontrole sama o sobě nepotvrzuje kompatibilitu. Přesný archiv ještě
potřebuje nový test spuštění a chování teleportu potřebuje popsaný test ve dvou.
Neznámou nebo změněnou verzi odmítne a zobrazí lokalizované upozornění. Tím není
ověřena každá možná kombinace s ostatními módy. Konzole, Game Pass, GOG, macOS
a Linux/Proton tato testovací verze nepodporuje.

Nastavení a HUD přímo ve hře jsou zatím **anglicky**. Existují katalogy pro
14 jazyků; chyby při startu používají dostupný jazyk Windows s anglickou
záložní variantou. Nejde zatím o kompletní jazykovou podporu herního rozhraní.

Nastavení a oblíbení peti jednotlivých savů zůstávají v
`%LOCALAPPDATA%/NMS-AutoPet`. Balíček neobsahuje cizí nastavení ani savy.
Poškozené nastavení se nepřepíše a automatika se spustí vypnutá; následné změny
mohou platit jen pro aktuální hraní.

Modul před aktivací svých herních funkcí vytvoří a ověří soukromou zálohu v
`%LOCALAPPDATA%/NMS-AutoPet/backups`. **Hra už v té chvíli běží:** jde o zálohu
před aktivací módu, nikoli před spuštěním hry nebo při vypnuté hře. Pokud
ověření selže, mód se neaktivuje. Původní savy nikdy neobnovuje, neupravuje ani
do nich nezapisuje. Pro první test si ponechte také samostatnou zálohu
vytvořenou při vypnuté hře.

Logy jsou v `%LOCALAPPDATA%/NMS-AutoPet/logs`. Pokud se pet neobjeví, zkontrolujte
zapnutí automatiky, povolené místo, režim výběru a běžné podmínky pro vyvolání.
Zastavení kvůli chybě nativního běhu vyžaduje restart hry. Chyba pouze při
zobrazení HUD hlášky automatické vyvolávání ani ukládání nastavení nevypne.

## Odinstalace nebo návrat k předchozí verzi

Vypněte hru a odstraňte pouze:

- `Binaries/scripts/CompanionAutoSummon.asi`
- `GAMEDATA/MODS/CompanionAutoSummon`

Pokud `Binaries/winmm.dll` potřebuje jiný ASI mód, ponechte ho. Odstranit ho lze
jen tehdy, když ho žádný další mód nepotřebuje a jeho hash stále odpovídá
loaderu z tohoto balíčku. Nemažte celé složky `Binaries`, `scripts`, `GAMEDATA`
ani jiné módy. Nastavení, oblíbení peti a zálohy zůstávají zachované. Při návratu
ke starší Python verzi nejprve odstraňte tento nativní modul a teprve potom
použijte původní launcher. Obě verze nikdy nespouštějte současně.

`manifest.json` obsahuje seznam souborů a jejich SHA-256. Ve složce `licenses/`
jsou licenční informace použitých knihoven. Ověření balíčku a testy mimo hru
nepotvrzují schválení Nexusem, živou kompatibilitu ani skutečné objevení peta.
