// server.js
import express from 'express';
import path from 'path';
import fs from "fs";
const app = express();
const port = process.env.PORT || 4000;
import { fileURLToPath } from 'url';
import axios from "axios";
import { v4 as uuidv4 } from 'uuid';
import cors from "cors";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename)

app.use(express.json())
app.use('/', express.static(path.join(__dirname, '/dist')));
app.use(cors())

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist/index.html'));
});

app.post("/generateImage", (req, res) => {
    const sendRequest = async () => {
        const data = req.body
        console.log(data)
        axios.post("http://localhost:5000/generate_collage", data, {responseType: 'stream'})
        .then((response) => {
            const id = uuidv4() 
            const savePath = path.resolve(__dirname, "dist/images", id+".jpg")
            const writer = fs.createWriteStream(savePath);

            response.data.pipe(writer);

            writer.on('finish', () => {
                console.log('Image downloaded and saved successfully!');
                res.json({image_address: "http://localhost:4000/images/"+id+".jpg"})
            });
        })
    }
    sendRequest()
})


app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});