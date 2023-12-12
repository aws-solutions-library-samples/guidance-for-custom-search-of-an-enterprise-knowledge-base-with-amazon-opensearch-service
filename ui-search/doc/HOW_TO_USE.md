# How to use this app

This article is to explain the basic usage of Custom Search of an Enterprise Knowledge Base ('Custom Search' in the following context). We assume that your app is successfully published.

## 1. App Configurations

When you first open the Custom Search web application, it automatically redirects you to the **App Configurations** page. The notifications suggest that several **essential variables** need to be configured before the app can be properly used.

They are:

- WebSocket URL: for conversations in sessions
- API Gateway URL: for file upload functions etc.
- S3 Bucket Name: for uploading files

These variables should be available immediately after your stacks are deployed.

You can always find the **App Configurations** page by clicking the link in the **Top Navigation**

## 2. File Uploads

After configured the app, especially the **S3 Bucket Name**, you can now proceed to the **Upload files** page by clicking the nav link **Upload files** on the side navigation panel.

You can pick an `Index Name` from the list or you can enter a new one of your choosing. Select a file. Press the `Confirm` button. When you see the notification that suggests successfully uploaded your file, you can proceed to **Add language models** page.

## 3. Add language model strategies

Click the nav link **Add language model strategies** on the side navigation panel. Here you can add Sagemaker Endpoint or Third Party APIs. Manage added language models in the `Language Model Strategies` Table.

## 4. Create a new session

Users can create a new session by clicking the **Create a new session** button on the side nav panel.

## 5. Have a conversation in a session

After the creation, you will be ushered to the newly created session. You can also pick an existing session by clicking any link under `Sessions` collapsible component on the side nav panel.

In a session, when `WSS` status turns green, you can start the conversation by typing your queries in the `Search Input`.
