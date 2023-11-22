# Use amplify to publish ui-search frontend website

## Prerequisite

### 1. Make sure you have installed the correct version of `node.js`

```bash
node -v
v16.20.1
npm -v
9.8.0
```

> If your system does not recognize the commands, please refer to the official doc for installation:
>
> - nodejs: https://nodejs.org/en/download
> - npm: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

### 2. Make sure you have installed `amplify-cli`

```bash
amplify -v
12.8.2
```

If your system does not recognize the command, please run the following code:

```bash
npm install -g @aws-amplify/cli
```

Note: You can always refer to the [user guide of Amplify](https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html) and [doc for Amplify cli](https://docs.amplify.aws/cli/) for more information.

## Deployment Overview

It is simple to publish this app with amplify, only 4 commands are needed.

```bash
amplify init
amplify hosting add
amplify publish -y
amplify console
```

Following the breakdowns for the first-timers.

## Init amplify

```bash
amplify init

# ? Enter a name for the project
uisearch (default)
# ? Initialize the project with the above configuration?
Yes
# ? select the authentication method you want to use:
AWS access keys
# then enter your accessKeyId and secretAccessKey
# and the according region

# ? Help improve Amplify CLI by sharing non-sensitive project configurations on failures
Yes
```

## Add amplify hosting

```bash
amplify hosting add

# ? Select the plugin module to execute …
❯ Hosting with Amplify Console (Managed hosting with custom domains, Continuous deployment)
# ? Choose a type
Manual deployment
```

## Publish the app

```bash
amplify publish -y
# ✔ Deployment complete!
https://dev.xxxx.amplifyapp.com
# visit your app ⬆️
```

\*\* While you are publishing the app, you can finish the last step below

### ‼️ VERY IMPORTANT: Don't forget to manage the amplify app

```bash
# launch your amplify console
amplify console
```

- Go to `Rewrites and redirects` under 'App Settings'
- Add a rule
- Write in 'Source address': `</^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>`
- Write in 'Target address': `/index.html`
- Press save

- ref: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html#redirects-for-single-page-web-apps-spa

---

# Local development

```bash
npm run start
```

# local build test

```bash
npm i -g serve
npm run build
serve build/ -s

```
