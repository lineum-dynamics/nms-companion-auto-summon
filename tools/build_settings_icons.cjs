/** Build original per-setting SVG glyphs and legacy DDS files; never deploy. */
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');

async function main() {
  const directory = path.resolve(__dirname, '../assets/ui');
  const names = ['automation', 'selection', 'biome', 'planet', 'station', 'anomaly'];
  const labels = ['Automatic summoning', 'Companion selection', 'Random: prefer matching biome',
    'Planets', 'Space stations', 'Space Anomaly'];
  const outputs = {};
  const tiles = [];
  for (const [index, name] of names.entries()) {
    const svg = await fs.readFile(path.join(directory, name + '.svg'));
    const { data, info } = await sharp(svg).resize(256, 256).ensureAlpha().raw()
      .toBuffer({ resolveWithObject: true });
    if (info.channels !== 4 || data.length !== 256 * 256 * 4) throw new Error('Invalid RGBA layout');
    const alpha = [];
    for (let i = 3; i < data.length; i += 4) alpha.push(data[i]);
    if (!alpha.includes(0) || !alpha.includes(255)) throw new Error('Missing transparency or solid fill');
    const header = Buffer.alloc(128);
    header.write('DDS ');
    for (const [offset, value] of [[4,124],[8,0x2100f],[12,256],[16,256],[20,1024],[28,1],
      [76,32],[80,0x41],[88,32],[92,0xff],[96,0xff00],[100,0xff0000],[104,0xff000000],[108,0x1000]]) {
      header.writeUInt32LE(value, offset);
    }
    const dds = Buffer.concat([header, data]);
    const png = await sharp(data, { raw: { width:256, height:256, channels:4 } }).png().toBuffer();
    const target = name.toUpperCase() + '.DDS';
    await fs.writeFile(path.join(directory, target), dds);
    await fs.writeFile(path.join(directory, name + '.png'), png);
    if (!(await fs.readFile(path.join(directory, target))).equals(dds)) throw new Error('DDS readback failed');
    outputs[target] = crypto.createHash('sha256').update(dds).digest('hex');
    const x = (index % 3) * 300, y = Math.floor(index / 3) * 260;
    tiles.push({ input: await sharp(png).resize(156,156).toBuffer(), left:x+72, top:y+30 });
    tiles.push({ input: Buffer.from(`<svg width="300" height="36"><text x="150" y="24" text-anchor="middle" fill="#eef6f8" font-family="Arial" font-size="16">${labels[index]}</text></svg>`), left:x, top:y+205 });
  }
  await sharp({ create: { width:900, height:520, channels:4, background:'#132832' } })
    .composite(tiles).png().toFile(path.join(directory, 'settings-icons-preview.png'));
  console.log(JSON.stringify({ original:true, deployed:false, outputs }));
}
main().catch(error => { console.error(error); process.exitCode=1; });
