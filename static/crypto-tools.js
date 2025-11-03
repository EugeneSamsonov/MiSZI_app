// Crypto Tools - Frontend only demo implementations
// NOTE: Educational-only ciphers. Do NOT use in production.


(function () {
	const $ = (sel) => document.querySelector(sel);
	const $$ = (sel) => Array.from(document.querySelectorAll(sel));

	const ui = {
		cards: null,
		fact: null,
		modal: null,
		backdrop: null,
		modalTitle: null,
		modalInput: null,
		modalKey: null,
		modalKeyField: null,
		modalHint: null,
		modalResult: null,
		statusBar: null,
		btnEncrypt: null,
		btnDecrypt: null,
		btnCopy: null,
		btnReset: null,
		btnExport: null,
		btnClose: null,
	};

	const L = {
		loading: 'Выполняется... ⏳',
		success: 'Готово ✅',
		error: 'Ошибка ❌',
		copied: 'Скопировано в буфер обмена 📋',
		cleared: 'Очищено 🧹',
		exported: 'Экспортировано в файл 💾',
	};

	function setStatus(msg, type = 'info') {
		ui.statusBar.textContent = msg;
		ui.statusBar.className = 'test_form_field small-info ' + type;
	}

	// No history/counters per revised UI

	// Encoding helpers
	const textEncoder = new TextEncoder();
	const textDecoder = new TextDecoder();
	function toBytes(s) { return textEncoder.encode(s); }
	function fromBytes(b) { return textDecoder.decode(b); }
	function toHex(bytes) { return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join(''); }
	function fromHex(hex) {
		hex = hex.replace(/[^0-9a-f]/gi, '');
		if (hex.length % 2) throw new Error('Неверный hex ключ');
		const out = new Uint8Array(hex.length / 2);
		for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
		return out;
	}
	function b64e(bytes) { return btoa(String.fromCharCode(...bytes)); }
	function b64d(b64) { return new Uint8Array(atob(b64).split('').map(c => c.charCodeAt(0))); }

	// Facts per cipher
	const FACTS = {
		caesar: 'Цезарь — один из древнейших шифров (I век до н.э.).',
		affine: 'Аффинный шифр — линейное преобразование по модулю 26.',
		des: 'DES — стандарт 1977 года; ныне считается устаревшим.',
		vigenere: 'Виженер — полиалфавитный шифр, известен как “несокрушимый”.',
		feistel: 'Сеть Фейстеля — базовый принцип многих блочных шифров.',
		transposition: 'Перестановки меняют порядок символов без замены.',
		rsa: 'RSA — предложен Ривестом, Шамиром и Адлеманом в 1977.',
		elgamal: 'ElGamal — основан на сложности дискретного логарифма.',
		ecc: 'ECC — сравнимая стойкость при меньших ключах, чем RSA.'
	};

	// Classical ciphers
	function caesarShift(str, key, decrypt=false) {
		const kRaw = parseInt(key, 10);
		if (isNaN(kRaw)) throw new Error('Ключ Цезаря должен быть числом');
		const RU = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ';
		const ru = RU.toLowerCase();
		const A=65,Z=90,a=97,z=122;
		return str.replace(/[A-Za-zА-Яа-яЁё]/g, ch => {
			const code = ch.charCodeAt(0);
			// Latin per-charset shift
			if (code>=A && code<=Z){ const m=26; const k=((kRaw%m)+m)%m; const s=decrypt?(m-k):k; return String.fromCharCode(A + (code-A + s)%m); }
			if (code>=a && code<=z){ const m=26; const k=((kRaw%m)+m)%m; const s=decrypt?(m-k):k; return String.fromCharCode(a + (code-a + s)%m); }
			// Cyrillic per-charset shift (33 letters incl. Ё)
			let idx = RU.indexOf(ch);
			if (idx!==-1){ const m=RU.length; const k=((kRaw%m)+m)%m; const s=decrypt?(m-k):k; return RU[(idx+s)%m]; }
			idx = ru.indexOf(ch);
			if (idx!==-1){ const m=ru.length; const k=((kRaw%m)+m)%m; const s=decrypt?(m-k):k; return ru[(idx+s)%m]; }
			return ch;
		});
	}

	function affineCipher(str, key, decrypt=false) {
		// key format: "a,b"
		const mKey = /^\s*(-?\d+)\s*,\s*(-?\d+)\s*$/.exec(String(key||''));
		if (!mKey) throw new Error('Ключ формата a,b (например 5,8)');
		let a = parseInt(mKey[1],10), b = parseInt(mKey[2],10);
		function mod(n, p){ return ((n%p)+p)%p; }
		function invAA(a, m){ a=mod(a,m); for(let x=1;x<m;x++) if ((a*x)%m===1) return x; throw new Error(`a и m=${m} должны быть взаимно просты`); }
		const RU = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ';
		const ru = RU.toLowerCase();
		const A=65,Z=90,aCode=97,z=122;
		return str.replace(/[A-Za-zА-Яа-яЁё]/g, ch => {
			const code = ch.charCodeAt(0);
			// Latin block
			if (code>=A && code<=Z){ const m=26; const aInv = decrypt? invAA(a,m):null; const x=code-A; const y = decrypt? mod(aInv*(x-b),m): mod(a*x+b,m); return String.fromCharCode(A+y); }
			if (code>=aCode && code<=z){ const m=26; const aInv = decrypt? invAA(a,m):null; const x=code-aCode; const y = decrypt? mod(aInv*(x-b),m): mod(a*x+b,m); return String.fromCharCode(aCode+y); }
			// Cyrillic block
			let idx = RU.indexOf(ch);
			if (idx!==-1){ const m=RU.length; const aInv = decrypt? invAA(a,m):null; const y = decrypt? mod(aInv*(idx-b),m): mod(a*idx+b,m); return RU[y]; }
			idx = ru.indexOf(ch);
			if (idx!==-1){ const m=ru.length; const aInv = decrypt? invAA(a,m):null; const y = decrypt? mod(aInv*(idx-b),m): mod(a*idx+b,m); return ru[y]; }
			return ch;
		});
	}

	function vigenereCipher(str, key, decrypt=false) {
		key = String(key || '').replace(/\s+/g, '');
		if (!key) throw new Error('Укажите ключ (буквы)');
		const RU = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ';
		const ru = RU.toLowerCase();
		const kLat = key.toUpperCase();
		const kRuU = key.split('').map(c=>RU.indexOf(c));
		const kRuL = key.split('').map(c=>ru.indexOf(c));
		let iLat=0, iRuU=0, iRuL=0;
		return str.replace(/[A-Za-zА-Яа-яЁё]/g, ch => {
			const code = ch.charCodeAt(0);
			// Latin
			if (code>=65 && code<=90){ const m=26; const s=(kLat.charCodeAt(iLat++ % kLat.length)-65+m)%m; const x=code-65; const y= decrypt? (x - s + m)%m : (x + s)%m; return String.fromCharCode(65+y); }
			if (code>=97 && code<=122){ const m=26; const s=(kLat.charCodeAt(iLat++ % kLat.length)-65+m)%m; const x=code-97; const y= decrypt? (x - s + m)%m : (x + s)%m; return String.fromCharCode(97+y); }
			// Cyrillic uppercase
			let idx = RU.indexOf(ch);
			if (idx!==-1){ const m=RU.length; const s = (kRuU[iRuU++ % kRuU.length] + m) % m; const y = decrypt? (idx - s + m)%m : (idx + s)%m; return RU[y]; }
			// Cyrillic lowercase
			idx = ru.indexOf(ch);
			if (idx!==-1){ const m=ru.length; const s = (kRuL[iRuL++ % kRuL.length] + m) % m; const y = decrypt? (idx - s + m)%m : (idx + s)%m; return ru[y]; }
			return ch;
		});
	}

	function transpositionCipher(str, key, decrypt=false) {
		key = String(key || '').replace(/\s+/g, '');
		if (!key) throw new Error('Укажите ключ (слово)');
		const order = key.split('').map((ch,i)=>({ch,i})).sort((a,b)=> a.ch.localeCompare(b.ch) || a.i-b.i).map(o=>o.i);
		const cols = key.length; const rows = Math.ceil(str.length/cols);
		if (!decrypt) {
			const grid = Array.from({length: rows}, (_,r)=> str.slice(r*cols,(r+1)*cols).padEnd(cols,' '));
			let out='';
			for (const colIdx of order) for (let r=0;r<rows;r++) out += grid[r][colIdx] || ' ';
			return out;
		} else {
			const len = rows*cols; const filled = str.padEnd(len,' ');
			const grid = Array.from({length: rows}, ()=> Array(cols).fill(' '));
			let p=0; for (const colIdx of order) for (let r=0;r<rows;r++) grid[r][colIdx]=filled[p++];
			return grid.map(row=>row.join('')).join('').trimEnd();
		}
	}

	// Toy Feistel network (demo only)
	function feistelCipher(str, keyHex, rounds=4, decrypt=false) {
		const key = fromHex(String(keyHex || '0f0e0d0c0b0a0908'));
		const isB64 = /^[A-Za-z0-9+/=]+$/.test(str) && (str.length%4===0);
		const bytes = decrypt && isB64 ? b64d(str) : toBytes(str);
		function F(r, k, i){
			let out = new Uint8Array(r.length);
			for (let j=0;j<r.length;j++) out[j] = r[j] ^ k[(j+i)%k.length] ^ ((j*31+i)&0xff);
			return out;
		}
		function process(block){
			let L = block.slice(0, block.length/2), R = block.slice(block.length/2);
			const rn = rounds|0;
			if (!decrypt) {
				for (let i=0;i<rn;i++){ const t = R; R = L.map((b,j)=> b ^ F(R,key,i)[j]); L = t; }
			} else {
				for (let i=rn-1;i>=0;i--){ const t = L; L = R.map((b,j)=> b ^ F(L,key,i)[j]); R = t; }
			}
			return new Uint8Array([...L, ...R]);
		}
		// pad to even length
		const padded = new Uint8Array(bytes.length % 2 ? bytes.length+1 : bytes.length);
		padded.set(bytes);
		let out = new Uint8Array(padded.length);
		for (let i=0;i<padded.length;i+=2){ out.set(process(padded.slice(i,i+2)), i); }
		const res = out.slice(0, bytes.length);
		return decrypt ? fromBytes(res) : b64e(res);
	}

	// Toy DES (extremely simplified, NOT real DES)
	function desDemo(str, keyStr, decrypt=false) {
		// XOR with repeated 8-byte key + byte rotation per char
		let key = toBytes(String(keyStr || '').padEnd(8,'0').slice(0,8));
		const isB64 = /^[A-Za-z0-9+/=]+$/.test(str) && (str.length%4===0);
		const data = decrypt && isB64 ? b64d(str) : toBytes(str);
		let out = new Uint8Array(data.length);
		for (let i=0;i<data.length;i++){
			// Use same rotation both ways so XOR inverts
			const rot = (i%8);
			let k = ((key[i%8] << rot) | (key[i%8] >>> (8-rot))) & 0xff;
			out[i] = data[i] ^ k;
		}
		return decrypt ? fromBytes(out) : b64e(out);
	}

	// Toy RSA (small integers)
	function egcd(a,b){ if(b===0) return [a,1,0]; const [g,x,y]=egcd(b,a%b); return [g,y,x-Math.floor(a/b)*y]; }
	function modInv(a,m){ const [g,x]=egcd(a,m); if(g!==1) throw new Error('Нет обратного'); return (x%m+m)%m; }
	function modPow(b,e,m){ let r=1n, base=BigInt(b)%BigInt(m), exp=BigInt(e), mod=BigInt(m); while(exp>0){ if(exp&1n) r=(r*base)%mod; base=(base*base)%mod; exp>>=1n;} return r; }
	function rsaEncrypt(str, pub){
		const {n,e}=pub; const bytes = toBytes(str); const out = new Uint8Array(bytes.length*2);
		for (let i=0;i<bytes.length;i++){
			const m = BigInt(bytes[i]);
			const c = modPow(m, BigInt(e), BigInt(n));
			const v = Number(c); // < n
			out[i*2] = (v>>8) & 0xff; out[i*2+1] = v & 0xff;
		}
		return b64e(out);
	}
	function rsaDecrypt(b64, priv){
		const {n,d}=priv; const data = b64d(b64); const out = new Uint8Array(data.length/2);
		for (let i=0;i<out.length;i++){
			const v = (data[i*2]<<8) | data[i*2+1];
			const m = modPow(BigInt(v), BigInt(d), BigInt(n));
			out[i] = Number(m & 0xffn);
		}
		return fromBytes(out);
	}
	function rsaDemoKeys(){
		// Fixed small primes for demo
		const p=137, q=149, n=p*q, phi=(p-1)*(q-1), e=65537 % phi; const d=modInv(e,phi);
		return { pub:{n,e}, priv:{n,d} };
	}

	// Toy ElGamal
	function elgamalParams(){ const p=30803, g=2; return {p,g}; }
	function elgamalKeypair(){ const {p,g}=elgamalParams(); const x=1234; const y = BigInt(g) ** BigInt(x) % BigInt(p); return {pub:{p,g,y:Number(y)}, priv:{p,g,x}}; }
	function elgamalEncrypt(str, pub){
		const {p,g,y}=pub; const P=BigInt(p), G=BigInt(g), Y=BigInt(y);
		const bytes = toBytes(str);
		const k=37n; const a = (G ** k) % P;
		const A = a.toString();
		const B = Array.from(bytes).map(b=> {
			const m = BigInt(b);
			const by = (Y ** k) % P;
			return Number((by * m) % P);
		});
		return { a: A, b: B };
	}
	function elgamalDecrypt(ct, priv){
		const {p,x}=priv; const P=BigInt(p);
		const a=BigInt(ct.a); const X=BigInt(x);
		const s = a ** X % P; const inv = modPow(s, BigInt(p-2), P);
		const out = new Uint8Array(ct.b.length);
		for (let i=0;i<ct.b.length;i++){
			const m = (BigInt(ct.b[i]) * inv) % P;
			out[i] = Number(m & 0xffn);
		}
		return fromBytes(out);
	}

	// Toy ECC over small curve y^2 = x^3 + ax + b mod p
	function eccParams(){ return { p: 233n, a: 1n, b: 1n, G: {x:4n, y:5n}, n: 239n } }
	function eccAdd(P,Q,params){ const {p,a}=params; if(!P) return Q; if(!Q) return P; if (P.x===Q.x && (P.y+Q.y)%p===0n) return null; const m = P.x===Q.x && P.y===Q.y
		? (3n*P.x*P.x + a) * modPow(2n*P.y, p-2n, p) % p
		: (Q.y - P.y) * modPow((Q.x - P.x + p)%p, p-2n, p) % p; const x = (m*m - P.x - Q.x) % p; const y = (m*(P.x - x) - P.y) % p; return {x:(x+p)%p, y:(y+p)%p}; }
	function eccMul(k,P,params){ let N=null, Q=P; let kk=BigInt(k); while(kk>0){ if(kk&1n) N=eccAdd(N,Q,params); Q=eccAdd(Q,Q,params); kk>>=1n; } return N; }
	function eccPRG(seed){ // simple LCG for demo
		let s = Number(seed % 2147483647n) || 1;
		return ()=> { s = (s * 48271) % 2147483647; return s & 0xff; };
	}
	function eccEncrypt(str, pub){
		const params=eccParams(); const {G}=params; const k=5n;
		const C1=eccMul(k,G,params); const Ky=eccMul(k,pub,params);
		const prg = eccPRG(Ky.x);
		const data = toBytes(str);
		const out = new Uint8Array(data.length);
		for (let i=0;i<data.length;i++) out[i] = data[i] ^ prg();
		return { C1:{x:String(C1.x), y:String(C1.y)}, data: b64e(out) };
	}
	function eccDecrypt(ct, priv){
		const params=eccParams(); const C1={x:BigInt(ct.C1.x), y:BigInt(ct.C1.y)}; const Ky=eccMul(priv, C1, params);
		const prg = eccPRG(Ky.x);
		const data = b64d(ct.data);
		const out = new Uint8Array(data.length);
		for (let i=0;i<data.length;i++) out[i] = data[i] ^ prg();
		return fromBytes(out);
	}
	function eccDemoKeys(){ const params=eccParams(); const d=7n; const Q=eccMul(d, params.G, params); return {pub:Q, priv:d}; }

	// Dispatcher
	const CIPHERS = {
		caesar: {
			name: 'Шифр Цезаря',
			placeholder: 'Ключ: число, напр. 3',
			encrypt: (t,k)=> caesarShift(t,k,false),
			decrypt: (t,k)=> caesarShift(t,k,true),
		},
		affine: {
			name: 'Аффинный шифр',
			placeholder: 'Ключ: a,b (например 5,8)',
			encrypt: (t,k)=> affineCipher(t,k,false),
			decrypt: (t,k)=> affineCipher(t,k,true),
		},
		des: {
			name: 'DES',
			placeholder: 'Ключ: 8 символов (вывод: base64)',
			encrypt: (t,k)=> desDemo(t,k,false),
			decrypt: (t,k)=> desDemo(t,k,true),
		},
		vigenere: {
			name: 'Шифр Виженера',
			placeholder: 'Ключ: слово, напр. LEMON',
			encrypt: (t,k)=> vigenereCipher(t,k,false),
			decrypt: (t,k)=> vigenereCipher(t,k,true),
		},
		feistel: {
			name: 'Сеть Фейстеля',
			placeholder: 'Ключ: hex, напр. 0f0e0d0c0b0a0908',
			encrypt: (t,k)=> feistelCipher(t,k,4,false),
			decrypt: (t,k)=> feistelCipher(t,k,4,true),
		},
		transposition: {
			name: 'Перестановка с ключом',
			placeholder: 'Ключ: слово, напр. SECRET',
			encrypt: (t,k)=> transpositionCipher(t,k,false),
			decrypt: (t,k)=> transpositionCipher(t,k,true),
		},
		rsa: {
			name: 'RSA',
			placeholder: 'Ген. ключей встроена (вывод: base64)',
			encrypt: (t)=> { const {pub}=rsaDemoKeys(); return String(rsaEncrypt(t,pub)); },
			decrypt: (t)=> { const {priv}=rsaDemoKeys(); return rsaDecrypt(String(t),priv); },
		},
		elgamal: {
			name: 'ElGamal',
			placeholder: 'Ген. ключей встроена (вывод: JSON)',
			encrypt: (t)=> { const {pub}=elgamalKeypair(); const ct=elgamalEncrypt(t,pub); return JSON.stringify(ct); },
			decrypt: (t)=> { const {priv}=elgamalKeypair(); return elgamalDecrypt(JSON.parse(t),priv); },
		},
		ecc: {
			name: 'ECC',
			placeholder: 'Ген. ключей встроена (вывод: JSON)',
			encrypt: (t)=> { const {pub}=eccDemoKeys(); const ct=eccEncrypt(t,pub); return JSON.stringify(ct); },
			decrypt: (t)=> { const {priv}=eccDemoKeys(); return eccDecrypt(JSON.parse(t),priv); },
		},
	};

	let currentCipher = 'caesar';
	const DEFAULT_KEYS = {
		caesar: '3',
		affine: '5,8',
		des: 'password',
		vigenere: 'LEMON',
		feistel: '0f0e0d0c0b0a0908',
		transposition: 'SECRET',
		rsa: '',
		elgamal: '',
		ecc: ''
	};

	function openModal(cipher){
		currentCipher = cipher;
		ui.modalTitle.textContent = CIPHERS[cipher].name;
		ui.modalHint.textContent = FACTS[cipher] || '';
		ui.modalKey.value = DEFAULT_KEYS[cipher] || '';
		ui.modalKeyField.style.display = (cipher==='rsa'||cipher==='elgamal'||cipher==='ecc') ? 'none' : '';
		ui.statusBar.textContent = '';
		ui.modalResult.value = '';
		ui.modal.setAttribute('aria-hidden','false');
		ui.backdrop.setAttribute('aria-hidden','false');
	}
	function closeModal(){
		ui.modal.setAttribute('aria-hidden','true');
		ui.backdrop.setAttribute('aria-hidden','true');
	}

	async function onAction(mode){
		try{
			const text = ui.modalInput.value;
			const key = ui.modalKey.value;
			if (!text) throw new Error('Введите текст');
			if (!['rsa','elgamal','ecc'].includes(currentCipher) && !key) throw new Error('Введите ключ');
			setStatus(L.loading, 'loading');
			await new Promise(r=>setTimeout(r, 50));
			let output;
			if (mode==='encrypt') output = CIPHERS[currentCipher].encrypt(text, key);
			else output = CIPHERS[currentCipher].decrypt(text, key);
			ui.modalResult.value = typeof output === 'string' ? output : String(output);
			setStatus(L.success, 'success');
		}catch(e){
			console.error(e);
			setStatus(`${L.error}: ${e.message||e}`, 'error');
		}
	}

	function copyResult(){
		navigator.clipboard.writeText(ui.modalResult.value||'').then(()=> setStatus(L.copied,'success')).catch(()=> setStatus(L.error,'error'));
	}
	function resetAll(){
		ui.modalInput.value=''; ui.modalKey.value=DEFAULT_KEYS[currentCipher]||''; ui.modalResult.value=''; setStatus(L.cleared,'success');
	}
	function exportResult(){
		const blob = new Blob([ui.modalResult.value||''], {type: 'text/plain;charset=utf-8'});
		const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='result.txt'; a.click(); URL.revokeObjectURL(a.href); setStatus(L.exported,'success');
	}

	function init(){
		ui.cards = $$('.crypto-card');
		ui.fact = $('#cipherFact');
		ui.modal = $('#cryptoModal');
		ui.backdrop = $('#modalBackdrop');
		ui.modalTitle = $('#modalTitle');
		ui.modalInput = $('#modalInput');
		ui.modalKey = $('#modalKey');
		ui.modalKeyField = $('#modalKeyField');
		ui.modalHint = $('#modalHint');
		ui.modalResult = $('#modalResult');
		ui.statusBar = $('#statusBar');
		ui.btnEncrypt = $('#modalEncrypt');
		ui.btnDecrypt = $('#modalDecrypt');
		ui.btnCopy = $('#modalCopy');
		ui.btnReset = $('#modalReset');
		ui.btnExport = $('#modalExport');
		ui.btnClose = $('#modalClose');

		ui.cards.forEach(card=>{
			card.addEventListener('mouseenter', ()=> ui.fact.textContent = FACTS[card.dataset.cipher] || '');
			card.addEventListener('focus', ()=> ui.fact.textContent = FACTS[card.dataset.cipher] || '');
			card.addEventListener('click', ()=> openModal(card.dataset.cipher));
		});
		ui.btnClose.addEventListener('click', closeModal);
		ui.backdrop.addEventListener('click', closeModal);
		ui.btnEncrypt.addEventListener('click', ()=> onAction('encrypt'));
		ui.btnDecrypt.addEventListener('click', ()=> onAction('decrypt'));
		ui.btnCopy.addEventListener('click', copyResult);
		ui.btnReset.addEventListener('click', resetAll);
		ui.btnExport.addEventListener('click', exportResult);

		// initial fact
		ui.fact.textContent = 'Выберите шифр, чтобы начать.';
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
	else init();
})();


