/** Rasterize original SVG and encode a legacy RGBA32 DDS; never deploy. */
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');

async function main() {
  const directory = path.resolve(__dirname, '../assets/ui');
  const svg = await fs.readFile(path.join(directory, 'companion-auto-summon-icon-v1.svg'));
  const width = 256;
  const { data: rgba, info } = await sharp(svg).resize(width, width).ensureAlpha()
    .raw().toBuffer({ resolveWithObject: true });
  if (info.width !== width || info.height !== width || info.channels !== 4 || rgba.length !== width * width * 4) {
    throw new Error('Unexpected original icon raster layout');
  }
  const alpha = [];
  for (let i = 3; i < rgba.length; i += 4) alpha.push(rgba[i]);
  if (!alpha.includes(0) || !alpha.includes(255) || !alpha.some(value => value > 0 && value < 255)) {
    throw new Error('Icon must contain transparent space, opaque fill and antialiased edges');
  }
  const header = Buffer.alloc(128);
  header.write('DDS ', 0, 'ascii');
  for (const [offset, value] of [
    [4, 124], [8, 0x2100f], [12, width], [16, width], [20, width * 4], [28, 1],
    [76, 32], [80, 0x41], [88, 32], [92, 0xff], [96, 0xff00],
    [100, 0xff0000], [104, 0xff000000], [108, 0x1000],
  ]) header.writeUInt32LE(value, offset);
  const dds = Buffer.concat([header, rgba]);
  const png = await sharp(rgba, { raw: { width, height: width, channels: 4 } }).png().toBuffer();
  const outputs = {
    'companion-auto-summon-icon-v1.png': png,
    'SETTINGS.DDS': dds,
  };
  for (const [name, data] of Object.entries(outputs)) {
    await fs.writeFile(path.join(directory, name), data);
    const readback = await fs.readFile(path.join(directory, name));
    if (!data.equals(readback)) throw new Error('Icon output readback failed');
  }
  console.log(JSON.stringify({ width, height: width, format: 'RGBA32', mipLevels: 1,
    transparent: true, deployed: false, outputs: Object.fromEntries(Object.entries(outputs).map(
      ([name, data]) => [name, { bytes: data.length, sha256: crypto.createHash('sha256').update(data).digest('hex') }])) }));
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
