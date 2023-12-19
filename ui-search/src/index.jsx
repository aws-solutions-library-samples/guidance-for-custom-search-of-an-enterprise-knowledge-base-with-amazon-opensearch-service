import {
  Density,
  Mode,
  applyDensity,
  applyMode,
} from '@cloudscape-design/global-styles';
import '@cloudscape-design/global-styles/index.css';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import LanguageModelStrategy from './components/LanguageModelStrategy';
import Landing from './components/Landing';
import Layout from './components/Layout';
import Session from './components/Session';
import UploadFiles from './components/UploadFiles';
import './index.css';
import reportWebVitals from './reportWebVitals';
import AppConfigs from './components/AppConfigs';
import { useRouteError } from 'react-router-dom';

applyMode(Mode.Light);
applyDensity(Density.Comfortable);

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <Landing /> },
      {
        path: 'app-configs',
        element: <AppConfigs />,
      },
      {
        path: 'session/:sessionId',
        element: <Session />,
      },
      {
        path: 'add-language-model-strategies',
        element: <LanguageModelStrategy />,
      },
      {
        path: 'upload-files',
        element: <UploadFiles />,
      },
      {
        path: 'about',
        element: <Landing withConfigs={false} />,
      },
      { path: '*', element: <PageNotFound /> },
    ],
  },
]);

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} fallbackElement={<Fallback />} />
  </React.StrictMode>
);

function Fallback() {
  return <p>Loading</p>;
}
function PageNotFound() {
  return <h4>404! Page Not Found...</h4>;
}
function ErrorPage() {
  const error = useRouteError();
  console.error(error);

  return (
    <div id="error-page">
      <h1>Oops!</h1>
      <p>Sorry, an unexpected error has occurred.</p>
      <p>
        <i>{error.statusText || error.message}</i>
      </p>
    </div>
  );
}
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
