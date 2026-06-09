const fs = require('node:fs/promises');
const path = require('node:path');
const { minify } = require('html-minifier-terser');
const CleanCSS = require('clean-css');
const { minify: minifyJs } = require('terser');
const { PurgeCSS } = require('purgecss');
const sharp = require('sharp');

const rootDir = path.resolve(__dirname, '..');
const distDir = path.join(rootDir, 'dist');

const SOURCE_FILES = {
  html: path.join(rootDir, 'index.html'),
  css: path.join(rootDir, 'styles.css'),
  js: path.join(rootDir, 'app.js')
};

const IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg']);
const IGNORE_DIRS = new Set(['.git', '.github', 'node_modules', 'dist', 'build']);

const purgeSafelist = {
  standard: ['active', 'scrolled', 'loading', 'hidden', 'animate-in', 'animate-prepare'],
  deep: [/^rating-/]
};

async function build() {
  await fs.rm(distDir, { recursive: true, force: true });
  await fs.mkdir(distDir, { recursive: true });

  const [rawHtml, rawCss, rawJs] = await Promise.all([
    fs.readFile(SOURCE_FILES.html, 'utf8'),
    fs.readFile(SOURCE_FILES.css, 'utf8'),
    fs.readFile(SOURCE_FILES.js, 'utf8')
  ]);

  const purgedCssResult = await new PurgeCSS().purge({
    content: [
      { raw: rawHtml, extension: 'html' },
      { raw: rawJs, extension: 'js' }
    ],
    css: [{ raw: rawCss }],
    safelist: purgeSafelist
  });

  const purgedCss = purgedCssResult[0]?.css ?? rawCss;
  const minifiedCss = new CleanCSS({ level: 2 }).minify(purgedCss).styles;

  const minifiedJsResult = await minifyJs(rawJs, {
    compress: true,
    mangle: true,
    format: { comments: false }
  });

  if (!minifiedJsResult.code) {
    throw new Error('JavaScript minification failed');
  }

  let htmlForBuild = rawHtml
    .replace(/href="styles\.css"/g, 'href="styles.min.css"')
    .replace(/src="app\.js"/g, 'src="app.min.js"');

  const webpMap = await optimizeImages();
  htmlForBuild = rewriteImageReferences(htmlForBuild, webpMap);
  htmlForBuild = addImageLazyLoading(htmlForBuild);

  const minifiedHtml = await minify(htmlForBuild, {
    collapseWhitespace: true,
    removeComments: true,
    minifyCSS: false,
    minifyJS: false,
    removeRedundantAttributes: true,
    removeEmptyAttributes: true,
    useShortDoctype: true
  });

  await Promise.all([
    fs.writeFile(path.join(distDir, 'index.html'), minifiedHtml, 'utf8'),
    fs.writeFile(path.join(distDir, 'styles.min.css'), minifiedCss, 'utf8'),
    fs.writeFile(path.join(distDir, 'app.min.js'), minifiedJsResult.code, 'utf8')
  ]);

  console.log('Build complete: dist/index.html, dist/styles.min.css, dist/app.min.js');
}

function addImageLazyLoading(html) {
  return html.replace(/<img\b([^>]*)>/gi, (match, attrs) => {
    let nextAttrs = attrs;
    if (!/\sloading\s*=\s*['"][^'"]+['"]/i.test(nextAttrs)) {
      nextAttrs += ' loading="lazy"';
    }
    if (!/\sdecoding\s*=\s*['"][^'"]+['"]/i.test(nextAttrs)) {
      nextAttrs += ' decoding="async"';
    }
    return `<img${nextAttrs}>`;
  });
}

async function optimizeImages() {
  const files = await collectFiles(rootDir);
  const imageFiles = files.filter(file => IMAGE_EXTENSIONS.has(path.extname(file).toLowerCase()));
  const map = new Map();

  await Promise.all(imageFiles.map(async (filePath) => {
    const relativePath = path.relative(rootDir, filePath).replace(/\\/g, '/');
    const outputOriginalPath = path.join(distDir, relativePath);
    await fs.mkdir(path.dirname(outputOriginalPath), { recursive: true });
    await fs.copyFile(filePath, outputOriginalPath);

    const webpRelativePath = relativePath.replace(/\.(png|jpe?g)$/i, '.webp');
    const outputWebpPath = path.join(distDir, webpRelativePath);
    await sharp(filePath).webp({ quality: 80, effort: 4 }).toFile(outputWebpPath);

    map.set(relativePath, webpRelativePath);
  }));

  return map;
}

function rewriteImageReferences(html, webpMap) {
  let output = html;

  for (const [originalPath, webpPath] of webpMap.entries()) {
    const escaped = escapeRegExp(originalPath);
    output = output.replace(new RegExp(`(["'])${escaped}(["'])`, 'g'), `$1${webpPath}$2`);
  }

  return output;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function collectFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (IGNORE_DIRS.has(entry.name)) continue;

    const absolutePath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectFiles(absolutePath));
    } else {
      files.push(absolutePath);
    }
  }

  return files;
}

build().catch(error => {
  console.error(error);
  process.exit(1);
});
