import {
  Box,
  Checkbox,
  ColumnLayout,
  Form,
  FormField,
  Input,
  Select,
  SelectProps,
  Textarea,
  Tiles,
  Toggle,
} from '@cloudscape-design/components';
import Button from '@cloudscape-design/components/button';
import Modal from '@cloudscape-design/components/modal';
import SpaceBetween from '@cloudscape-design/components/space-between';
import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import {
  DEFAULT_WORK_FLOW,
  DEFAULT_WORK_MODE,
  OPTIONS_SEARCH_ENGINE,
  OPTIONS_WORK_MODE,
} from 'src/constants';
import useIndexNameList from 'src/hooks/useIndexNameList';
import useInput from 'src/hooks/useInput';
import useLsAppConfigs from 'src/hooks/useLsAppConfigs';
import useLsLanguageModelList from 'src/hooks/useLsLanguageModelList';
import useLsSessionList from 'src/hooks/useLsSessionList';
import useToggle from 'src/hooks/useToggle';
import { useSessionStore } from 'src/stores/session';
import { DEFAULT_CHAT_SYSTEM_PROMPT } from 'src/utils/PROMPT_TEMPLATES';
import {
  ILocConfigs,
  ILocLlmData,
  IWorkFLow,
  SEARCH_ENGINE,
  WORK_MODE,
  WORK_MODULE,
} from 'src/types';
import Divider from './Divider';

const SIZE = 's';
export type ILanguageValues = (typeof OPTIONS_LANGUAGE)[number]['value'];
const OPTIONS_LANGUAGE = [
  { label: '简体中文', value: 'chinese' },
  { label: '繁体中文', value: 'chinese-tc' },
  { label: 'English', value: 'english' },
] as const;

export type ISearchMethodValues = (typeof SEARCH_METHOD)[number]['value'];
const SEARCH_METHOD = [
  { label: 'vector', value: 'vector' },
  { label: 'text', value: 'text' },
  { label: 'mix', value: 'mix' },
] as const;

export default function ModalCreateSession({ dismissModal, modalVisible }) {
  const { addSession } = useSessionStore();
  const { lsLanguageModelList } = useLsLanguageModelList();
  const { lsSessionList, lsGetOneSession } = useLsSessionList();
  const { appConfigs } = useLsAppConfigs();
  const [name, bindName, resetName] = useInput('');
  const [sessionTemplateOpt, setSessionTemplateOpt] =
    useState<SelectProps.Option>();

  // CHAT Module
  const [
    chatSystemPrompt,
    bindChatSystemPrompt,
    resetChatSystemPrompt,
    setChatSystemPrompt,
  ] = useInput(DEFAULT_CHAT_SYSTEM_PROMPT);
  const [workFlow, setWorkFlow] = useState<IWorkFLow>(DEFAULT_WORK_FLOW);
  const [workMode, _, resetWorkMode, setWorkMode] =
    useInput<WORK_MODE>(DEFAULT_WORK_MODE);
  const [
    isCheckedKnowledgeBase,
    bindKnowledgeBase,
    resetKnowledgeBase,
    setIsCheckedKnowledgeBase,
  ] = useToggle(true);
  const [
    isCheckedTextRAGOnlyOnMultiModal,
    bindTextRAGOnlyOnMultiModal,
    resetTextRAGOnlyOnMultiModal,
    setIsCheckedTextRAGOnlyOnMultiModal,
  ] = useToggle(false, (checked) => checked && setIsCheckedKnowledgeBase(true));

  const [searchEngine, bindSearchEngine, resetSearchEngine, setSearchEngine] =
    useInput<SEARCH_ENGINE>(SEARCH_ENGINE.opensearch);

  const [llmData, setLLMData] = useState<ILocLlmData>(lsLanguageModelList[0]);
  const [role, bindRole, resetRole, setRole] = useInput();

  const [language, setLanguage] = useState<ILanguageValues>(
    OPTIONS_LANGUAGE[0].value
  );
  useLsAppConfigs();

  const [
    taskDefinition,
    bindTaskDefinition,
    resetTaskDefinition,
    setTaskDefinition,
  ] = useInput();
  const [outputFormat, bindOutputFormat, resetOutputFormat, setOutputFormat] =
    useInput();

  const [indexName, setIndexName] = useState('');
  const [indexNameList, loadingIndexNameList, refreshIndexNameList] =
    useIndexNameList(modalVisible);
  const [searchMethod, setSearchMethod] = useState<ISearchMethodValues>(
    SEARCH_METHOD[0].value
  );
  const [txtTopK, setTxtDocsNum] = useState(0);
  const [vecDocsScoreThresholds, setVecDocsScoreThresholds] = useState(0);
  const [txtDocsScoreThresholds, setTxtDocsScoreThresholds] = useState(0);
  const [vecTopK, setTopK] = useState(3);
  const [contextRounds, setContextRounds] = useState(3);

  const [isCheckedScoreQA, bindScoreQA, resetScoreQA, setIsCheckedScoreQA] =
    useToggle(true);
  const [isCheckedScoreQD, bindScoreQD, resetScoreQD, setIsCheckedScoreQD] =
    useToggle(true);
  const [isCheckedScoreAD, bindScoreAD, resetScoreAD, setIsCheckedScoreAd] =
    useToggle(true);
  const [isCheckedEditPrompt, setIsCheckedEditPrompt] = useState(false);

  const [prompt, setPrompt] = useState('');

  useEffect(() => {
    let partRole = role ? `${role}. ` : '';
    const partTask = taskDefinition ? `${taskDefinition}. ` : '';
    const partOutputFormat = outputFormat || '';
    if (role) {
      if (language === 'english') {
        partRole = `You are a ${partRole}`;
        setPrompt(
          `${partRole}${partTask}${partOutputFormat}\n\nQuestion:{question}\n=========\n{context}\n=========\nAnswer:`
        );
      } else {
        partRole = `你是一名${partRole}`;
        setPrompt(
          `${partRole}${partTask}${partOutputFormat}\n\n问题:{question}\n=========\n{context}\n=========\n答案:`
        );
      }
    }
  }, [role, taskDefinition, outputFormat, language]);

  const resetAllFields = useCallback(() => {
    // reset fields after the creation completes
    // NOTE: add code when adding new inputs
    resetName();
    resetSearchEngine();
    resetWorkMode();
    setWorkFlow(DEFAULT_WORK_FLOW);
    resetTextRAGOnlyOnMultiModal();
    resetChatSystemPrompt();
    setLLMData(undefined);
    resetRole();
    resetTaskDefinition();
    resetOutputFormat();
    resetKnowledgeBase();
    // resetMapReduce();
    setIndexName('');
    setSearchMethod(SEARCH_METHOD[0].value);
    setTopK(3);
    setContextRounds(3);
    setTxtDocsNum(0);
    setVecDocsScoreThresholds(0);
    setTxtDocsScoreThresholds(0);
    // resetIndexName();
    resetScoreQA();
    resetScoreQD();
    resetScoreAD();
    setSessionTemplateOpt(undefined);
    setLoading(false);
    setValidating(false);
    setPrompt('');
    setIsCheckedEditPrompt(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (sessionTemplateOpt?.value) {
      // Setting template
      // NOTE: add code when adding new inputs
      const {
        configs: {
          // name,
          searchEngine,
          workMode,
          workFlowLocal,
          isCheckedTextRAGOnlyOnMultiModal,
          llmData,
          role,
          language,
          taskDefinition,
          outputFormat,
          isCheckedKnowledgeBase,
          indexName,
          vecTopK,
          contextRounds,
          searchMethod,
          txtTopK,
          vecDocsScoreThresholds,
          txtDocsScoreThresholds,
          isCheckedScoreQA,
          isCheckedScoreQD,
          isCheckedScoreAD,
          isCheckedEditPrompt,
        },
      } = lsGetOneSession(sessionTemplateOpt.value!, lsSessionList);
      // CHAT prompt
      let chatSystemPrompt = '';
      // RAG prompt
      let ragSystemPrompt = '';
      const workFlow = workFlowLocal.map((flow) => {
        if (flow.module === WORK_MODULE.CHAT)
          chatSystemPrompt = flow.systemPrompt;
        if (flow.module === WORK_MODULE.RAG)
          ragSystemPrompt = flow.systemPrompt;
        return flow.module;
      });

      // setName(name);
      // NOTE: add code when adding new inputs
      if (searchEngine !== undefined) setSearchEngine(searchEngine);
      if (workMode !== undefined) setWorkMode(workMode);
      if (workFlow !== undefined) setWorkFlow(workFlow);
      if (isCheckedTextRAGOnlyOnMultiModal !== undefined)
        setIsCheckedTextRAGOnlyOnMultiModal(isCheckedTextRAGOnlyOnMultiModal);
      if (chatSystemPrompt !== undefined) {
        if (workMode === DEFAULT_WORK_MODE) {
          setChatSystemPrompt(undefined);
        } else {
          setChatSystemPrompt(chatSystemPrompt);
        }
      }
      if (llmData !== undefined) setLLMData(llmData);
      if (role !== undefined) setRole(role);
      if (language !== undefined) setLanguage(language);
      if (taskDefinition !== undefined) setTaskDefinition(taskDefinition);
      if (outputFormat !== undefined) setOutputFormat(outputFormat);

      if (isCheckedKnowledgeBase !== undefined)
        setIsCheckedKnowledgeBase(isCheckedKnowledgeBase);
      // setIsCheckedMapReduce(isCheckedMapReduce);

      if (indexName !== undefined) setIndexName(indexName);
      if (vecTopK !== undefined) setTopK(Number(vecTopK));
      if (contextRounds !== undefined) setContextRounds(contextRounds);
      if (searchMethod !== undefined) setSearchMethod(searchMethod);
      if (txtTopK !== undefined) setTxtDocsNum(Number(txtTopK));
      if (vecDocsScoreThresholds !== undefined)
        setVecDocsScoreThresholds(vecDocsScoreThresholds);
      if (txtDocsScoreThresholds !== undefined)
        setTxtDocsScoreThresholds(txtDocsScoreThresholds);

      if (isCheckedScoreQA !== undefined) setIsCheckedScoreQA(isCheckedScoreQA);
      if (isCheckedScoreQD !== undefined) setIsCheckedScoreQD(isCheckedScoreQD);
      if (isCheckedScoreAD !== undefined) setIsCheckedScoreAd(isCheckedScoreAD);
      if (isCheckedEditPrompt !== undefined)
        setIsCheckedEditPrompt(isCheckedEditPrompt);
      if (ragSystemPrompt !== undefined) setPrompt(ragSystemPrompt);
    } else {
      setSessionTemplateOpt(undefined);
    }
  }, [sessionTemplateOpt, lsSessionList]);

  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);

  return (
    <Modal
      header="Session Configurations"
      onDismiss={dismissModal}
      visible={modalVisible}
      size="large"
      footer={
        <Box>
          <Box float="left">
            <Button onClick={resetAllFields}>Reset all fields</Button>
          </Box>
          <Box float="right">
            <Button
              variant="primary"
              loading={loading}
              iconName="insert-row"
              onClick={async () => {
                try {
                  setLoading(true);
                  setValidating(true);

                  // NOTE: add code when adding new inputs
                  const sessionData: Omit<ILocConfigs, 'sessionId'> = {
                    name,
                    searchEngine,
                    workMode,
                    workFlowLocal: workFlow.map((mod) => ({
                      module: mod,
                      systemPrompt:
                        mod === WORK_MODULE.CHAT ? chatSystemPrompt : prompt,
                    })),
                    isCheckedTextRAGOnlyOnMultiModal,
                    llmData,
                    role,
                    language,
                    taskDefinition,
                    outputFormat,
                    isCheckedKnowledgeBase,
                    indexName,
                    vecTopK,
                    searchMethod,
                    txtTopK,
                    vecDocsScoreThresholds,
                    txtDocsScoreThresholds,
                    isCheckedScoreQA,
                    isCheckedScoreQD,
                    isCheckedScoreAD,
                    contextRounds,
                    isCheckedEditPrompt,
                    tokenContentCheck: appConfigs.tokenContentCheck,
                    responseIfNoDocsFound: appConfigs.responseIfNoDocsFound,
                  };

                  if (!llmData?.strategyName) {
                    return toast.error('Please select language model strategy');
                  }

                  await addSession(sessionData);
                  dismissModal();
                  resetAllFields();
                } catch (error) {
                  console.error(error);
                } finally {
                  setLoading(false);
                }
              }}
            >
              Create a session
            </Button>
          </Box>
        </Box>
      }
    >
      <form onSubmit={(e) => e.preventDefault()}>
        <Form>
          <SpaceBetween size={SIZE}>
            <ColumnLayout columns={2}>
              <FormField
                label="Session Name"
                description="Define a session name for future references"
              >
                <Input {...bindName} placeholder="Data search" />
              </FormField>

              <FormField
                label="Refer to an existing session or a template"
                description="Select a template or an existing session as template"
              >
                <Select
                  selectedOption={sessionTemplateOpt}
                  onChange={({ detail }) =>
                    setSessionTemplateOpt(detail.selectedOption)
                  }
                  options={lsSessionList.map(({ text, sessionId }) => ({
                    value: sessionId,
                    label: text,
                  }))}
                />
              </FormField>
            </ColumnLayout>

            <Divider />

            <FormField
              stretch
              label="Work Mode"
              description="Please select a work mode"
            >
              <Tiles
                columns={2}
                value={workMode}
                items={OPTIONS_WORK_MODE}
                onChange={({ detail: { value } }) => {
                  setWorkMode(value as WORK_MODE);
                  setWorkFlow(
                    OPTIONS_WORK_MODE.find((m) => m.value === value).workFlow
                  );
                  if (value === DEFAULT_WORK_MODE) {
                    setChatSystemPrompt(undefined);
                  }
                }}
              />
            </FormField>

            {workMode !== DEFAULT_WORK_MODE && (
              <>
                <FormField
                  stretch
                  label="System Prompt for CHAT module"
                  description="Please provide your system prompt for CHAT module"
                >
                  <Textarea
                    {...bindChatSystemPrompt}
                    rows={4}
                    placeholder="System prompt for CHAT module"
                  />
                </FormField>
                <FormField
                  stretch
                  constraintText="Check to bypass CHAT module when it is NOT a multi-modal query"
                >
                  <Toggle {...bindTextRAGOnlyOnMultiModal}>
                    Bypass Chat module
                  </Toggle>
                </FormField>
              </>
            )}

            <Divider />

            <FormField stretch label="Search Engine">
              <Tiles {...bindSearchEngine} items={OPTIONS_SEARCH_ENGINE} />
            </FormField>

            <SpaceBetween direction="vertical" size="xl">
              <ColumnLayout columns={3}>
                <FormField
                  label="Language Model Strategy"
                  description="Please select a strategy"
                  errorText={
                    validating &&
                    !llmData?.strategyName &&
                    'Please provide Index Name'
                  }
                >
                  <Select
                    empty="Add llm if no options present"
                    selectedOption={{
                      label:
                        llmData?.strategyName ||
                        llmData?.modelName ||
                        llmData?.recordId,
                    }}
                    onChange={({ detail }) => {
                      setLLMData(
                        detail.selectedOption.value as unknown as ILocLlmData
                      );
                    }}
                    options={lsLanguageModelList.map((item) => ({
                      label:
                        item.strategyName || item.modelName || item.recordId,
                      value: item as any,
                    }))}
                  />
                </FormField>
                <FormField
                  label="Language"
                  description="Select a language for conversation"
                >
                  <Select
                    selectedOption={{ value: language }}
                    onChange={({ detail }) =>
                      setLanguage(
                        detail.selectedOption.value as ILanguageValues
                      )
                    }
                    options={OPTIONS_LANGUAGE}
                  />
                </FormField>
                <FormField
                  label="Context Rounds"
                  description="Search with how many rounds of context"
                >
                  <Input
                    step={1}
                    type="number"
                    value={contextRounds.toString()}
                    onChange={({ detail }) => {
                      setContextRounds(Number(detail.value));
                    }}
                  />
                </FormField>
              </ColumnLayout>

              <Divider />

              <FormField constraintText="Chat Mode is activated when knowledge base is NOT specified">
                <Toggle
                  {...bindKnowledgeBase}
                  disabled={isCheckedTextRAGOnlyOnMultiModal}
                >
                  Knowledge Base
                </Toggle>
              </FormField>
              {!isCheckedKnowledgeBase ? null : (
                <SpaceBetween direction="vertical" size="s">
                  <ColumnLayout columns={3}>
                    <FormField
                      label="Index Name"
                      stretch
                      errorText={
                        validating && !indexName && 'Please provide Index Name'
                      }
                    >
                      <Select
                        onFocus={refreshIndexNameList}
                        empty="Upload a file if no options present"
                        onChange={({ detail }) =>
                          setIndexName(detail.selectedOption.value)
                        }
                        loadingText="loading index names"
                        statusType={
                          loadingIndexNameList ? 'loading' : 'finished'
                        }
                        selectedOption={{ value: indexName }}
                        options={indexNameList.map((name) => ({
                          value: name,
                        }))}
                      />
                    </FormField>
                    <FormField stretch label="Search method">
                      <Select
                        selectedOption={{ value: searchMethod }}
                        onChange={({ detail }) =>
                          setSearchMethod(
                            detail.selectedOption.value as ISearchMethodValues
                          )
                        }
                        options={SEARCH_METHOD}
                      />
                    </FormField>
                    <FormField
                      stretch
                      label="Threshold for vector search"
                      constraintText="Float number between 0 and 1"
                      errorText={
                        vecDocsScoreThresholds >= 0 &&
                        vecDocsScoreThresholds <= 1
                          ? ''
                          : 'A number between 0 and 1'
                      }
                    >
                      <Input
                        onBlur={() =>
                          vecDocsScoreThresholds !== 0 &&
                          !vecDocsScoreThresholds
                            ? setVecDocsScoreThresholds(0)
                            : null
                        }
                        step={0.01}
                        type="number"
                        value={vecDocsScoreThresholds.toString()}
                        onChange={({ detail }) => {
                          setVecDocsScoreThresholds(Number(detail.value));
                        }}
                      />
                    </FormField>
                  </ColumnLayout>
                  <ColumnLayout columns={3}>
                    <FormField
                      stretch
                      label="Number of doc for vector search"
                      constraintText="Integer between 0 and 200"
                      errorText={
                        vecTopK >= 0 && vecTopK <= 200
                          ? ''
                          : 'A number between 0 and 200'
                      }
                    >
                      <Input
                        onBlur={() =>
                          vecTopK !== 0 && !vecTopK ? setTopK(0) : null
                        }
                        step={1}
                        type="number"
                        inputMode="decimal"
                        value={vecTopK.toString()}
                        onChange={({ detail }) => {
                          setTopK(Number(detail.value));
                        }}
                      />
                    </FormField>
                    <FormField
                      stretch
                      label="Number of doc for text search"
                      constraintText="Integer between 0 and 200"
                      errorText={
                        txtTopK >= 0 && txtTopK <= 200
                          ? ''
                          : 'A number between 0 and 200'
                      }
                    >
                      <Input
                        onBlur={() =>
                          txtTopK !== 0 && !txtTopK ? setTxtDocsNum(0) : null
                        }
                        step={1}
                        type="number"
                        inputMode="decimal"
                        value={txtTopK.toString()}
                        onChange={({ detail }) => {
                          setTxtDocsNum(Number(detail.value));
                        }}
                      />
                    </FormField>
                    <FormField
                      stretch
                      label="Threshold for text search"
                      constraintText="Float number between 0 and 1"
                      errorText={
                        txtDocsScoreThresholds >= 0 &&
                        txtDocsScoreThresholds <= 1
                          ? ''
                          : 'A number between 0 and 1'
                      }
                    >
                      <Input
                        onBlur={() =>
                          txtDocsScoreThresholds !== 0 &&
                          !txtDocsScoreThresholds
                            ? setTxtDocsScoreThresholds(0)
                            : null
                        }
                        step={0.01}
                        type="number"
                        value={txtDocsScoreThresholds.toString()}
                        onChange={({ detail }) => {
                          setTxtDocsScoreThresholds(Number(detail.value));
                        }}
                      />
                    </FormField>
                  </ColumnLayout>
                  <FormField stretch label="Calculate Confidence Scores">
                    <SpaceBetween direction="horizontal" size="xxl">
                      <Checkbox {...bindScoreQA}>Query-Answer score</Checkbox>
                      <Checkbox {...bindScoreQD}>Query-Doc scores</Checkbox>
                      <Checkbox {...bindScoreAD}>Answer-Doc scores</Checkbox>
                    </SpaceBetween>
                  </FormField>
                </SpaceBetween>
              )}

              <Divider />

              <SpaceBetween size={SIZE}>
                {!isCheckedEditPrompt ? (
                  <>
                    <FormField
                      stretch
                      label="Role Name"
                      description="Please determine the role"
                    >
                      <Input {...bindRole} placeholder="a footwear vendor" />
                    </FormField>
                    <FormField
                      stretch
                      label="Task Definition"
                      description="Please provide your task definition"
                    >
                      <Textarea
                        {...bindTaskDefinition}
                        rows={2}
                        placeholder="recommend appropriate footwear to the customer"
                      />
                    </FormField>
                    <FormField
                      stretch
                      label="Output Format"
                      description="Please provide your output format"
                    >
                      <Textarea
                        {...bindOutputFormat}
                        rows={1}
                        placeholder="answer in English"
                      />
                    </FormField>
                  </>
                ) : null}

                {!isCheckedEditPrompt ? (
                  <FormField
                    stretch
                    label="RAG Prompt Summary"
                    description="Generated automatically by the values of Role Name, Task Definition and Output Format"
                    secondaryControl={
                      <SpaceBetween size="xxs">
                        <Button
                          variant="primary"
                          iconName="edit"
                          onClick={() => {
                            setRole('');
                            setTaskDefinition('');
                            setOutputFormat('');
                            setIsCheckedEditPrompt(true);
                          }}
                        >
                          Edit Prompt
                        </Button>
                        <small style={{ color: 'grey' }}>
                          ⚠️ You can edit your prompt freely, however, role
                          name, task definition and output format will not be
                          displayed
                        </small>
                      </SpaceBetween>
                    }
                  >
                    <Textarea value={prompt} disabled rows={6} />
                  </FormField>
                ) : (
                  <FormField
                    stretch
                    label="Edit Prompt"
                    description="Customise your RAG prompt as you please"
                  >
                    <Textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.detail.value)}
                      rows={10}
                    />
                  </FormField>
                )}
              </SpaceBetween>
            </SpaceBetween>
          </SpaceBetween>
        </Form>
      </form>
    </Modal>
  );
}
