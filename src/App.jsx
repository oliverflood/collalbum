
  import './App.css'
  import AutoScrollGallery from './AutoScrollGallery.jsx';
  import { useEffect, useRef } from 'react';

  const clientId = "c7d69233368e4745b7032ab8837ae6d4";
  const redirectUri = "http://localhost:3000/";

  let hasRunRef = false;

  const generateRandomString = (length) => {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const values = window.crypto.getRandomValues(new Uint8Array(length));
    return values.reduce((acc, x) => acc + possible[x % possible.length], "");
  };

  const sha256 = async (plain) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(plain);
    return window.crypto.subtle.digest('SHA-256', data);
  };

  const base64encode = (input) => {
    return btoa(String.fromCharCode(...new Uint8Array(input)))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_');
  };

  const initAuth = async (codeVerifier) => {
    const hashed = await sha256(codeVerifier);
    const codeChallenge = base64encode(hashed);

    window.localStorage.setItem('code_verifier', codeVerifier);

    const scope = 'user-read-private user-read-email user-top-read';
    const authUrl = new URL("https://accounts.spotify.com/authorize");

    const params = {
      response_type: 'code',
      client_id: clientId,
      scope,
      code_challenge_method: 'S256',
      code_challenge: codeChallenge,
      redirect_uri: redirectUri,
    };

    authUrl.search = new URLSearchParams(params).toString();
    window.location.href = authUrl.toString();
  };

  const getToken = async code => {

    // stored in the previous step
    const codeVerifier = localStorage.getItem('code_verifier');
  
    const url = "https://accounts.spotify.com/api/token";
    const payload = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: clientId,
        grant_type: 'authorization_code',
        code,
        redirect_uri: redirectUri,
        code_verifier: codeVerifier,
      }),
    }
  
    const body = await fetch(url, payload);
    const response = await body.json();
  
    localStorage.setItem('access_token', response.access_token);
  }
  

  const App = () => {
    const login = () => {
      const codeVerifier = generateRandomString(64);
      initAuth(codeVerifier);
    };

    useEffect(() => {
      if (hasRunRef) return;
      hasRunRef = true;
    
      const access_token = localStorage.getItem('access_token');
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
    
      const fetchTopTracks = async (token) => {
        const artDictionary = new Map()

        var attempts = 0

        while (artDictionary.size < 25 && attempts < 6) {
          const response = await fetch("https://api.spotify.com/v1/me/top/tracks?limit=50&offset="+ (attempts * 50).toString() +"&time_range=long_term", {
              method: "GET",
              headers: {
                  "Authorization": "Bearer " + access_token
              }
          });


          const data = await response.json() 
          data.items.forEach(element => {
            if (!artDictionary[element.album.images[0].url] && artDictionary.size < 25) {
              artDictionary.set(element.album.images[0].url, 1)
            } 
          });

          attempts += 1
        }

        let image_urls = Array.from(artDictionary.keys())
        console.log(image_urls)
        while (image_urls.length < 25) {
          let randomIndex = Math.floor(Math.random() * image_urls.length)
          image_urls.push(image_urls[randomIndex])
        }

        var response_object = {images: image_urls}

        const response2 = await fetch("http://localhost:4000/generateImage", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify(response_object)
        })
        const data2 = await response2.json()
        
        console.log(data2.image_address)
        document.getElementById("collage-image").src = data2.image_address
      };



    
      const init = async () => {
        if (access_token) {
          console.log("Access token exists! Fetching top tracks...");
          await fetchTopTracks(access_token);
        } else if (code) {
          console.log("Access token missing! Getting token...")
          await getToken(code);
          
          const newToken = localStorage.getItem('access_token');
          if (newToken) {
            console.log("New access token generated! Fetching now...")
            window.history.replaceState({}, document.title, '/'); // remove code from URL
            await fetchTopTracks(newToken);
          }
        } else {
          console.log("No token or code — waiting for user to click login");
        }
      };
    
      init();
    }, []);

    return (
      <>
        <div id="collage-image-container">
          <img id="collage-image" src="https://upload.wikimedia.org/wikipedia/en/5/5b/Chromakopia_CD_cover.jpg" />
        </div>

        <AutoScrollGallery />

        <button onClick={login} className="spotify-button">
          <img
            className="spotify-logo"
            src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
            alt="Spotify Logo"
          />
          Sign in with Spotify
        </button>
      </>
    );
  };

  export default App;
