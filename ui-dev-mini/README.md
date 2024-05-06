# user guide

## App configs

### Env variables

Open file: `/.env`
And add values to variables:

- `REACT_APP_URL_WSS` url for websocket
- and `REACT_APP_KB_INDEX_NAME` knowledge base index name for queries

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
