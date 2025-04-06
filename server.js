// server.js
import express from 'express';
import path from 'path';
import fs from "fs";
const app = express();
const port = process.env.PORT || 3000;
import { fileURLToPath } from 'url';
import axios from "axios";
import { v4 as uuidv4 } from 'uuid';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename)

app.use('/public', express.static(path.join(__dirname, '/public')));
app.use(express.json())

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/main.html'));
});

app.post("/generateImage", (req, res) => {
    axios.get("https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_1280.jpg", {responseType: 'stream'})//, {body: req.body})
    .then((response) => {
        const id = uuidv4() 
        const savePath = path.resolve(__dirname, "public", id+".jpg")
        const writer = fs.createWriteStream(savePath);

        response.data.pipe(writer);

        writer.on('finish', () => {
            console.log('Image downloaded and saved successfully!');
            res.json({image_address: "http://localhost:3000/public/"+id})
        });
    })
})

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});