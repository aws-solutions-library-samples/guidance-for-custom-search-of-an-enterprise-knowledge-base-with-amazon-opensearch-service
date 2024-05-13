# SmartSearch Mini v3.3 User Guide

## App configs

### Env variables

Open file: `/.env`
And add values to variables:

- `REACT_APP_URL_WSS` url for websocket
- and `REACT_APP_KB_INDEX_NAME` knowledge base index name for queries

### Default Session Configs

You can configure default session for the websocket API here `/src/constants/DEFAULT_SESSION.js`

Please checkout [User Guide v3.3](https://quip-amazon.com/4YEBAuvWd3GQ/Intelligent-Search-V33) API section for more details re how to configure each value.

### Start local server

```bash
# install dependencies
npm i
# or
yarn

# start server
npm run start
# or
yarn start
```

### Notes

- Please checkout the key logic of websocket in the file `/src/hooks/useRAGWebSocket.js`
