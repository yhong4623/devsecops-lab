const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/calc', (req, res) => {
  const expr = req.query.expr || '0';
  // 危險：直接 eval 使用者輸入（教學用途）
  const result = eval(expr);
  res.json({ result });
});

app.listen(3000, () => console.log('Running on port 3000'));
