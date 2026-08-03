const fs = require('fs');
const vm = require('vm');
const path = 'c:/Users/BACS_TI_Col/Documents/Desarrollo/ERP_BACS/static/js/formulario.js';
const code = fs.readFileSync(path, 'utf8');
try {
  new vm.Script(code, {filename: path});
  console.log('PARSE_OK');
} catch (e) {
  console.error('PARSE_ERROR', e && e.message);
  console.error(e.stack);
  process.exit(1);
}
