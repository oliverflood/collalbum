// server.js
import express from 'express';
import path from 'path';
const app = express();
const port = process.env.PORT || 3000;
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename)

app.use('/public', express.static(path.join(__dirname, '/public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/main.html'));
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});