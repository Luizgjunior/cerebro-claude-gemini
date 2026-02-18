const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

// Serve Static Frontend
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/index.html'));
});

const MEMORY_FILE = 'C:/Users/Luiz/CORE_MEMORY.md';

const BRAINS = [
  { id: 'gemini', name: 'Gemini CLI', icon: '🌌', color: '#4285f4' },
  { id: 'claude', name: 'Claude Code', icon: '🎭', color: '#d97757' }
];

app.get('/api/brains', (req, res) => {
  res.json(BRAINS);
});

app.get('/api/memory', (req, res) => {
  try {
    const memory = fs.readFileSync(MEMORY_FILE, 'utf8');
    res.json({ content: memory });
  } catch (err) {
    res.status(500).json({ error: 'Erro ao ler arquivo de memória' });
  }
});

app.post('/api/chat', (req, res) => {
  const { message, brain } = req.body;
  
  // Comando dinâmico baseado no cérebro escolhido
  let command = '';
  if (brain === 'claude') {
    // Usando 'claude' diretamente (assume que está no PATH)
    command = `claude "${message}"`;
  } else {
    command = `gemini-call.bat "${message}"`;
  }
  
  console.log(`Executing on ${brain.toUpperCase()}: ${command}`);
  
  exec(command, { cwd: 'C:/Users/Luiz' }, (error, stdout, stderr) => {
    // Capturamos stdout mesmo com erro, pois CLIs costumam mandar logs para stderr
    const output = stdout || stderr;
    res.json({ output: output });
  });
});

app.listen(PORT, () => {
  console.log(`AIOS Server running on http://localhost:${PORT}`);
});
