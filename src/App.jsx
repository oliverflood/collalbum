
import './App.css'
import { useEffect } from 'react';

const clientId = "867d29a6e7e9406c9ebe3efd80da2f06";
const redirectUri = "http://localhost:3000/";

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

const getToken = async (code) => {
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
  };

  const body = await fetch(url, payload);
  const response = await body.json();

  localStorage.setItem('access_token', response.access_token);
};

const App = () => {
  const login = () => {
    const codeVerifier = generateRandomString(64);
    initAuth(codeVerifier);
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const access_token = localStorage.getItem('access_token');

    const fetchTopTracks = async (access_token) => {
      const res = await fetch(
        "https://api.spotify.com/v1/me/top/tracks?limit=20",
        {
          headers: {
            Authorization: "Bearer " + access_token,
          },
        }
      );

      const data = await res.json();
      console.log("Top tracks:", data);
    };

    const init = async () => {
      let access_token = localStorage.getItem("access_token");
  
      if (access_token) {
        console.log("first " + access_token);
        fetchTopTracks(access_token);
        console.log("after " + access_token);
      } else if (code) {
        await getToken(code); // This should save token to localStorage
        access_token = localStorage.getItem("access_token");
        
        if (access_token) {
          fetchTopTracks(access_token);
        }
      }
    };

    init();
  }, []);

  return (
    <>
      <nav>
        <img src="https://upload.wikimedia.org/wikipedia/en/5/5b/Chromakopia_CD_cover.jpg" />
      </nav>

      <div className="scroll-container">
        {[1, 2, 3, 4, 5].map((_, i) => (
          <img
            key={i}
            src="https://i.scdn.co/image/ab67616d0000b2736b219c8d8462bfe254a20469"
            alt="Album Cover Art"
            height="320px"
            width="320px"
          />
        ))}
      </div>

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
