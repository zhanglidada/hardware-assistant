// 将 json 格式的字符串转为 jsonl 模式

const fs = require('fs');
 
// 读cpu
let jsonc = fs.readFileSync('../src/mock/cpu_data.json', 'utf-8');
jsonc = JSON.parse(jsonc);
 
// 将 json 数组转换成字符串
let strc = '';
for (const item of jsonc) {
	// 必须使用 \n 换行区别每个记录
	strc += JSON.stringify(item) + "\n";
}

fs.writeFileSync('../src/mock/cpu_data_cvt.json', strc);

// 读 gpu
let jsong = fs.readFileSync('../src/mock/gpu_data.json', 'utf-8');
jsong = JSON.parse(jsong);
 
// 将 json 数组转换成字符串
let strg = '';
for (const item of jsong) {
	// 必须使用 \n 换行区别每个记录
	strg += JSON.stringify(item) + "\n";
}

fs.writeFileSync('../src/mock/gpu_data_cvt.json', strg);

// 读 phone
let jsonp = fs.readFileSync('../src/mock/phone_data.json', 'utf-8');
jsonp = JSON.parse(jsonp);
 
// 将 json 数组转换成字符串
let strp = '';
for (const item of jsonp) {
	// 必须使用 \n 换行区别每个记录
	strp += JSON.stringify(item) + "\n";
}
 
// 保存到本地
fs.writeFileSync('../src/mock/phone_data_cvt.json', strp);