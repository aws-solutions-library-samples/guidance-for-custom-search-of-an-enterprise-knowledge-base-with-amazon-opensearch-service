import logo from './logo.svg';
import './App.css';
import React from 'react';

import {Route, BrowserRouter} from 'react-router-dom';
import {Switch} from 'react-router';
// import SearchMain from './pages/MainSearch'
import SearchMainKNN from './pages/MainSearchKNN'
import SearchFAQ from './pages/MainSearchKNNFAQ'
import LTR from './pages/LearningToRank'
import SearchDoc from './pages/MainSearchDoc'
import FileUpload from './pages/FileUpload'
import GenerateReport from './pages/GenerateReport'

function App() {
    return (
        <BrowserRouter>
            <Switch>
                {/* <Route exact path="/" component={SearchMain}/> */}
                {/*<Route exact path="/" component={SearchMainKNN}/>*/}
                <Route exact path="/" component={SearchFAQ}/>
                <Route exact path="/search_doc" component={SearchDoc}/>
                <Route exact path="/ltr" component={LTR}/>
                <Route exact path="/file_upload" component={FileUpload}/>
                <Route exact path="/gen_report" component={GenerateReport}/>
            </Switch>
        </BrowserRouter>
    );
}

export default App;
