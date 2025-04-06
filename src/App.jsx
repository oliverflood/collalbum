
  import './App.css'
  import AutoScrollGallery from './AutoScrollGallery.jsx';
  import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';

  const clientId = "c7d69233368e4745b7032ab8837ae6d4";
  const redirectUri = "https://collalbum.guessmybuild.com/";

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
    window.location.href = window.location.href.split("?")[0]
  }
  

  const CollageImage = forwardRef((props, ref) => {

    const [collageContent, setCollageContent] = useState(
        <h2 className="loading_box">
            <p className="loading_text">This is where your music collage will appear!!</p>
        </h2>
    );

    const [loadingMessage, setLoadingMessage] = useState(
        <></>
    )

    const loadingCollageContent = () => {
      setCollageContent(
        <h2 className="loading_box">
            <p className="loading_text">Loading music collage...</p>
            <span className="loader"></span>
        </h2>
      );
      setLoadingMessage (
        <p className="loadingMessageContent">Creating your collage...</p>
      );
    }

    useImperativeHandle (ref, () => ({
      buttonClicked: () => {
        const access_token = localStorage.getItem('access_token');
        if (access_token) {
          console.log("Access token exists! Fetching top tracks...");
          loadingCollageContent();
          fetchTopTracks(access_token);
        }
      },
    }))

    const fetchTopTracks = async (access_token) => {
      const artDictionary = new Map()

      var attempts = 0

      while (attempts < 6) {
        const response = await fetch("https://api.spotify.com/v1/me/top/tracks?limit=50&offset="+ (attempts * 50).toString() +"&time_range=long_term", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + access_token
            }
        });

        const data = await response.json() 
        data.items.forEach(element => {
          if (!artDictionary[element.album.images[0].url]) {
            artDictionary.set(element.album.images[0].url, 1)
          } 
        });

        attempts += 1
      }

      let image_urls = Array.from(artDictionary.keys())
      console.log(image_urls)
      while (image_urls.length < 36) {
        let randomIndex = Math.floor(Math.random() * image_urls.length)
        image_urls.push(image_urls[randomIndex])
      }

      var response_object = {images: image_urls}

      const response2 = await fetch("/generateImage", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(response_object)
      })
      const data2 = await response2.json()
      
      setCollageContent(<img id="collage-image" src={data2.image_address} />); 
      setLoadingMessage(<p className="loadingMessageContent">Your collage link: <a href={data2.image_address}>{data2.image_address}</a></p>);
    };
 
    return (
      <>
        <div id="collage-image-container">
          { collageContent }
        </div>

        <div id="link_container">
          { loadingMessage }
        </div>
      </>
    );
  });


  const ActionButton = ({login, handleClick}) => {
    var spotifyButton = (<button onClick={login} className="spotify-button">
      <img
        className="spotify-logo"
        src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg"
        alt="Spotify Logo"
      />
      Sign in with Spotify
    </button>);

    var createButton = (<button onClick={handleClick} className="create-button">
      <img
        className="create-collage-logo"
        src="https://static.vecteezy.com/system/resources/previews/026/631/857/non_2x/collage-icon-symbol-design-illustration-vector.jpg"
        alt="Collage Logo"
      />
      Create Collage!
    </button>);

    const [button, setButton] = useState(spotifyButton)

    useEffect(() => {
      const access_token = localStorage.getItem('access_token');
      if (access_token) {
        setButton(createButton);
      } else {
        setButton(spotifyButton);
      }
    }, []);

    return (
      <div className="buttonHolder">
        {button}
      </div>
    );
  }

  const SigninMessage = () => {
    const [loginElem, setLoginElem] = useState(<div></div>)

    useEffect(() => {
      const access_token = localStorage.getItem('access_token');
      if (access_token) {
        fetch("https://api.spotify.com/v1/me", {
          method: "GET",
          headers: {
            "Authorization": "Bearer " + access_token
          }
        }).then((response) => {
          console.log(response);
          return response.json();
        }).then((data) => {
          console.log(data)
          var user = data.email.split("@")[0]
          setLoginElem(<div className="username">Hello, {user}!</div>)
        })
      }
    }, [])

    return (
      <>
        {loginElem}
      </>
    )

  }

  const App = () => {
    const login = () => {
      const codeVerifier = generateRandomString(64);
      initAuth(codeVerifier);
    };

    const componentRef = useRef();

    const handleClick = () => {
      componentRef.current.buttonClicked();
    };

    useEffect(() => {
      if (hasRunRef) return;
      hasRunRef = true;
    
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
    
      const init = async () => {
        if (code) {
          console.log("Access token missing! Getting token...")
          await getToken(code);
          
        } else {
          console.log("No token or code — waiting for user to click login");
        }
      };
    
      init();
    }, []);

    return (
      <>
        <AutoScrollGallery />

        <CollageImage ref={componentRef}/>

        <SigninMessage />

        <ActionButton login={login} handleClick={handleClick}/>
      </>
    );
  };

  export default App;
