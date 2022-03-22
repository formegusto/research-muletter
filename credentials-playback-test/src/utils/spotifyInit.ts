export default function spotifyInit() {
  window.onSpotifyWebPlaybackSDKReady = () => {
    // const token =
    //   "BQA1PmVrzYOHDLFpdVFVd9mh-VHhk-AfvE31fTV0l9BjxF9DBSaJvsJmvwMl63EUxSAp62rgRB_sOaWstYg-PI84_db5rGmgRGNY0JA";
    const token = "";
    const player = new window.Spotify.Player({
      name: "MuLetter Play",
      getOAuthToken: (cb: any) => {
        cb(token);
      },
      volume: 0.5,
    });

    player.addListener("ready", ({ device_id }: any) => {
      console.log("Ready with Device ID", device_id);
    });

    player.addListener("not_ready", ({ device_id }: any) => {
      console.log("Device ID has gone offline", device_id);
    });

    player.connect();
  };

  const script = document.createElement("script");
  script.src = "https://sdk.scdn.co/spotify-player.js";
  script.async = true;
  document.body.appendChild(script);
}
