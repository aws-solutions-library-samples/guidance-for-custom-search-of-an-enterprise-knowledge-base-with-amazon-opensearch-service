import React, {useState, useEffect} from 'react';
import {
    Button,
    SpaceBetween,
    FormField, Grid, Form, Container, Header, Input, Textarea,
} from '@cloudscape-design/components';
import {CustomAppLayout} from './common/common-components';
import {MyNavigation} from './common/mynavigation';

import axios from 'axios'

import {
    mainapi,
    HEADERS,
} from '../pages/common/constants'


function App({distributions}) {

    const [report_content, setReportContent] = useState("")
    const generate_report = (e, query, vector_index, role, task_definition, hard_rules) => {

        // const prompt_template = "你是一名ROLE。\n" +
        //     "现在需要你根据上下文进行以下任务 {question} \n" +
        //     "=======\n" +
        //     "{content}\n" +
        //     "=======\n" +
        //     "请必须要遵守以下规定: HARD_RULES。"

        const _request_url = mainapi + '/langchain_processor_qa'

        const payload = {
            "query": query,
            "index": vector_index,
            "top_k": "3",
            "language": "chinese",
        }

        // if task_definition is NOT ""/null/undefined
        if (task_definition) {
            payload["prompt"] = task_definition
        }

        axios({method: 'GET', url: _request_url, headers: HEADERS, params: payload}).then(response => {
            console.log(response);
            setReportContent(response.data.suggestion_answer)
        })
    }

    const GenerateReportPanel = () => {

        const [query, setQuery] = useState("");
        const [vector_index, setIndex] = useState("smart_search_qa_test");
        const [role, setRole] = useState("分析师");
        const [task_definition, setTask] = useState("");
        const [hard_rules, setHardRules] = useState("");

        return (
            <Form>
                <Container
                    header={
                        <Header variant="h3">
                            Report Generation Input
                        </Header>
                    }
                >
                    <SpaceBetween direction="vertical" size="l">
                        <FormField label="Query">
                            <Textarea onChange={({detail}) => setQuery(detail.value)}
                                      value={query}
                                      placeholder="Input report generation requirement"
                                      rows={3}
                                      ariaRequired={true}
                            />
                        </FormField>
                        <FormField label="Index">
                            <Input value={vector_index}
                                   onChange={({detail}) => setIndex(detail.value)}
                                   placeholder="Input Vector Index in OpenSearch"
                            />
                        </FormField>
                        <FormField label="Role Definition" description="Define role LLM will act as">
                            <Input value={role}
                                   onChange={({detail}) => setRole(detail.value)}
                                   placeholder="Input role like 金融分析师/程序员等"
                            />
                        </FormField>
                        <FormField label="Task Definition" description="Define what task you need LLM to do">
                            <Textarea value={task_definition}
                                      onChange={({detail}) => setTask(detail.value)}
                                      placeholder="Input task definition"
                                      rows={10}
                            />
                        </FormField>
                        <FormField label="Hard Rules" description="Define hard rule you need LLM to follow">
                            <Textarea value={hard_rules}
                                      onChange={({detail}) => setHardRules(detail.value)}
                                      placeholder="Input rules"
                                      rows={10}
                            />
                        </FormField>

                        <Button variant="primary"
                                onClick={(e) => generate_report(
                                    e,
                                    query,
                                    vector_index,
                                    role,
                                    task_definition,
                                    hard_rules
                                )}>{'Generate Report'}</Button>
                    </SpaceBetween>
                </Container>
            </Form>
        )
    }

    const OutputPanel = () => {
        return (
            <Textarea
                // onChange={({detail}) => setReportContent(detail.value)}
                value={report_content}
                placeholder="LLM and Financial Data based report will be generated and display here"
                readOnly
                rows={50}
            />
        )
    }

    function MainPanel(distributions) {

        return (
            <>
                <Grid
                    gridDefinition={[
                        {colspan: {l: 12, m: 12, default: 12}},
                        {colspan: {l: 6, m: 6, default: 6}},
                        {colspan: {l: 6, m: 6, default: 6}},
                    ]}
                >
                    <Button variant="link" disabled>{''}</Button>
                    <GenerateReportPanel/>
                    <OutputPanel/>
                </Grid>
            </>
        )
    }


    return (
        <CustomAppLayout
            navigation={<MyNavigation/>}
            content={<MainPanel distributions={distributions}/>}
            contentType="table"
            stickyNotifications
        />
    );
}

function SearchMain() {
    return (
        <App/>
    );
}

export default SearchMain;
