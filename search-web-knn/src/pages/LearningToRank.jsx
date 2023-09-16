// import logo from '../logo.svg';
import '../App.css';

import React, {useState} from 'react';
import {CustomAppLayout} from './common/common-components';
import {Button, SpaceBetween, Input, Grid, FormField, Textarea} from '@cloudscape-design/components';
import {MyNavigation} from './common/mynavigation';

import axios from 'axios'

import {
    mainapi,
    HEADERS,
    post_HEADERS,
    opensearch_api,
    opensearch_region,
} from '../pages/common/constants'

const api = mainapi


function MainContent({}) {
    const MainSearch = () => {
        const [tableName, setTabelName] = useState("FeedbackRecordsSEWCFAQ");
        const [numberOfDay, setNumberOfDay] = useState(30);
        const [indexName, setIndexName] = useState("sewc_faq");
        const [modelName, setModelName] = useState("");

        const [featureSetName, setFeatureSetName] = useState("features_question");
        const [featureNames, setFeatureNames] = useState("question");
        const [submitSuccessNotification, setSubmitSuccessNotification] = useState("");

        function CreatAndDeplyMLModel(
            table_name,
            before_day,
            index_name,
            feature_set_name,
            feature_set,
            model_name,
        ) {
            const creatModelAndDeplyMLModelPayload = {
                "Method": "create_ltr_model",
                "dynamodb": {
                    "table_name": table_name,
                    "before_day": before_day,
                    "region": "us-east-2"
                },
                "opensearch": {
                    "host": opensearch_api,
                    "index_name": index_name,
                    "region": opensearch_region,
                    // "username": opensearch_username,
                    // "password": opensearch_password,
                    "feature_set_name": feature_set_name,
                    "feature_set": feature_set,
                    "model_name": model_name
                }
            }
            console.log(creatModelAndDeplyMLModelPayload)
            axios({
                method: 'POST',
                url: api,
                data: creatModelAndDeplyMLModelPayload,
                headers: HEADERS
            }).then(response => {
                console.log(response);
                setSubmitSuccessNotification('The training job was submitted, the new machine learning model could be used within several minutes')
            })
        }

        return (
            <SpaceBetween size="s" direction="vertical">
                <SpaceBetween size="xxs" direction="vertical">
                    <h3>DynamoDB Related Parameter</h3>
                    <FormField
                        constraintText="dynamodb table name (str)"
                        label="Table Name"
                    >
                        <Input
                            onChange={({detail}) => setTabelName(detail.value)}
                            value={tableName}
                            placeholder="dynamodb table name"
                        />
                    </FormField>

                    <FormField
                        constraintText="number of the day (int)"
                        label="Day"
                    >
                        <Input
                            onChange={({detail}) => setNumberOfDay(detail.value)}
                            value={numberOfDay}
                            placeholder="numberof the day"
                        />
                    </FormField>

                    <h3>OpenSearch Related Parameter</h3>

                    <FormField
                        constraintText="index name (str)"
                        label="Index Name"
                    >
                        <Input
                            onChange={({detail}) => setIndexName(detail.value)}
                            value={indexName}
                            placeholder="index name"
                        />
                    </FormField>

                    <FormField
                        constraintText="model name (str)"
                        label="Model Name"
                    >
                        <Input
                            onChange={({detail}) => setModelName(detail.value)}
                            value={modelName}
                            placeholder="model name"
                        />
                    </FormField>


                    <FormField
                        constraintText="feature set name (str)"
                        label="Feature Set Name"
                    >
                        <Input
                            onChange={({detail}) => setFeatureSetName(detail.value)}
                            value={featureSetName}
                            placeholder="feature set name"
                        />
                    </FormField>

                    <FormField
                        constraintText="feature names (str)"
                        label="Feature Names"
                    >
                        <Textarea
                            onChange={({detail}) => setFeatureNames(detail.value)}
                            value={featureNames}
                            placeholder="feature names"
                        />
                    </FormField>

                    <h3></h3>

                    <Button variant="primary" onClick={() => CreatAndDeplyMLModel(
                        tableName, numberOfDay, indexName, featureSetName, featureNames, modelName
                    )}>{'Submit'}</Button>

                    <h3>{submitSuccessNotification}</h3>

                </SpaceBetween>
            </SpaceBetween>
        );
    }

    return (
        <Grid
            gridDefinition={[
                {colspan: {l: 4, m: 4, default: 12}},
                {colspan: {l: 4, m: 4, default: 12}},
                {colspan: {l: 4, m: 4, default: 12}},
            ]}
        >
            <Button variant="link" disabled>{''}</Button>
            <MainSearch/>
        </Grid>
    );
}


const navItems = [
    {
        type: 'link',
        text: 'Search',
    },
    {
        type: 'link',
        text: 'Mange',
    },
];

function App({}) {
    const [toolsOpen, setToolsOpen] = useState(false);

    return (
        <CustomAppLayout
            // navigation={<Navigation activeHref="#/distributions" />}
            navigation={<MyNavigation/>}
            // notifications={<Notifications successNotification={true} />}
            // breadcrumbs={<Breadcrumbs />}
            content={<MainContent/>}
            contentType="table"
            // tools={<ToolsContent />}
            // toolsOpen={toolsOpen}
            // onToolsChange={({ detail }) => setToolsOpen(detail.open)}
            stickyNotifications
        />
    );
}


function LTR() {
    return (
        <App/>
    );
}

export default LTR;