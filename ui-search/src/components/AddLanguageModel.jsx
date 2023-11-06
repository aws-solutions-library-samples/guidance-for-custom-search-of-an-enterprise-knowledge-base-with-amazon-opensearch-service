// @ts-nocheck
import {
  Box,
  Button,
  Container,
  Form,
  FormField,
  Header,
  Input,
  Select,
  SpaceBetween,
  Table,
  Tiles,
} from '@cloudscape-design/components';
import { useCallback, useState } from 'react';
import useInput from 'src/hooks/useInput';
import useLsLanguageModelList from 'src/hooks/useLsLanguageModelList';
import { genRandomNum } from 'src/utils/genUID';

const SIZE = 'l';

const TYPE = { sagemaker: 'sagemaker_endpoint', thirdParty: 'third_party_api' };
const SAGEMAKER_MODEL_TYPE = [
  { label: 'llama2', value: 'llama2' },
  { label: 'none llama2', value: 'none_llama2' },
];
const THIRD_PARTY_APIS = [
  // { label: 'ChatGPT', value: 'ChatGPT' },
  // { label: 'Claude', value: 'Claude' },
  // { label: 'ChatGLM', value: 'ChatGLM' },
  // { label: 'WestLake', value: 'WestLake' },
  { label: 'Bedrock', value: 'bedrock_api' },
];
const THIRD_PARTY_API_MODEL_NAME = [
  { label: 'Claude2', value: 'Claude2' },
  { label: 'Titan', value: 'Titan' },
];

const AddLanguageModel = () => {
  const [type, setType] = useState(TYPE.sagemaker);
  const [sagemakerEndpoint, bindSagemakerEndpoint, resetSagemakerEndpoint] =
    useInput('');
  const [embeddingEndpoint, bindEmbeddingEndpoint, resetEmbeddingEndpoint] =
    useInput('');
  const [thirdPartyModelType, setThirdPartyApiOption] = useState(
    THIRD_PARTY_APIS[0].value
  );
  const [sagemakerModelType, setSagemakerModelType] = useState(
    SAGEMAKER_MODEL_TYPE[0].value
  );
  const [endpointOrApiKey, bindEndpointOrApiKey, resetEndpointOrApiKey] =
    useInput('');
  const [thirdPartyModelName, setThirdPartyModelName] = useState(
    THIRD_PARTY_API_MODEL_NAME[0].value
  );
  const [modelName, bindModelName, resetModelName] = useInput('');

  const resetForm = useCallback(() => {
    resetSagemakerEndpoint();
    resetEmbeddingEndpoint();
    resetEndpointOrApiKey();
    resetModelName();
  }, []);

  const {
    lsLanguageModelList,
    lsAddLanguageModelItem,
    lsClearLanguageModelList,
    lsDelLanguageModelItem,
  } = useLsLanguageModelList();

  return (
    <SpaceBetween size={SIZE}>
      <SpaceBetween size="s">
        <Container header={<Header variant="h2">Language Models</Header>}>
          <SpaceBetween size={SIZE}>
            <Table
              items={lsLanguageModelList}
              variant="borderless"
              empty={
                <Box
                  margin={{ vertical: 'xs' }}
                  textAlign="center"
                  color="inherit"
                >
                  <SpaceBetween size="m">
                    <b>No resources</b>
                  </SpaceBetween>
                </Box>
              }
              columnDefinitions={[
                // {
                //   recordId: 'recordId',
                //   header: 'ID',
                //   width: 90,
                //   cell: (item) => item.recordId,
                // },
                {
                  id: 'modelName',
                  header: 'Model Name',
                  isRowHeader: true,
                  width: 150,
                  cell: (item) => item.modelName,
                },
                {
                  id: 'type',
                  header: 'Type',
                  width: 120,
                  cell: (item) => item.type,
                },
                {
                  id: 'modelType',
                  header: 'Model Type',
                  width: 50,
                  cell: (item) => item.modelType,
                },
                {
                  id: 'sagemakerEndpoint',
                  header: 'Sagemaker Endpoint',
                  width: 200,
                  cell: (item) => item.sagemakerEndpoint || 'n/a',
                },
                {
                  id: 'embeddingEndpoint',
                  header: 'EmbeddingEndpoint',
                  width: 200,
                  cell: (item) => item.embeddingEndpoint || 'n/a',
                },
                {
                  id: 'endpointOrApiKey',
                  header: 'Endpoint / API Key',
                  width: 200,
                  cell: (item) => item.endpointOrApiKey || 'n/a',
                },
                {
                  id: 'operations',
                  header: 'Operations',
                  width: 20,
                  cell: (item) => (
                    <SpaceBetween size="xxs">
                      <Button
                        iconName="remove"
                        onClick={() => lsDelLanguageModelItem(item.recordId)}
                      />
                    </SpaceBetween>
                  ),
                },
              ]}
            />
            <Box float="right">
              <Button onClick={lsClearLanguageModelList}>
                Delete all language models
              </Button>
            </Box>
          </SpaceBetween>
        </Container>
      </SpaceBetween>
      <Container header={<Header variant="h2">Add a language model</Header>}>
        <form onSubmit={(e) => e.preventDefault()}>
          <Form
            variant="embedded"
            actions={
              <SpaceBetween alignItems="center" size={SIZE}>
                <Button
                  variant="primary"
                  iconName="status-positive"
                  onClick={() => {
                    try {
                      let values;
                      if (type === TYPE.sagemaker) {
                        // Sagemaker endpoint
                        values = {
                          type,
                          // *** different items
                          sagemakerEndpoint,
                          embeddingEndpoint,
                          modelType: sagemakerModelType,
                          // *** backend doesn't care about these
                          modelName: modelName || sagemakerEndpoint,
                          recordId: `${endpointOrApiKey}-${genRandomNum()}`,
                        };
                      } else {
                        // Third Party APIs
                        values = {
                          type,
                          // *** different items
                          endpointOrApiKey,
                          modelType: thirdPartyModelType,
                          modelName: thirdPartyModelName,
                          // *** backend doesn't care about these
                          recordId: `${thirdPartyModelName}-${genRandomNum()}`,
                        };
                      }
                      console.log(values);
                      lsAddLanguageModelItem(values);
                      resetForm();
                    } catch (error) {
                      console.error(error);
                    }
                  }}
                >
                  Confirm
                </Button>
              </SpaceBetween>
            }
          >
            <SpaceBetween size={SIZE}>
              <FormField stretch label="Please select the endpoint type">
                <Tiles
                  value={type}
                  onChange={(e) => setType(e.detail.value)}
                  items={[
                    {
                      value: TYPE.sagemaker,
                      label: 'Sagemaker Endpoint',
                      description: 'A brief description of Sagemaker Endpoint',
                    },
                    {
                      value: TYPE.thirdParty,
                      label: 'Third Party APIs',
                      description:
                        'Options are ChatGPT, Claude, ChatGLM, WestLake',
                    },
                  ]}
                />
              </FormField>

              {type === TYPE.sagemaker ? (
                <>
                  <FormField label="Model Type">
                    <Select
                      selectedOption={{ value: sagemakerModelType }}
                      onChange={({ detail }) =>
                        setSagemakerModelType(detail.selectedOption.value)
                      }
                      options={SAGEMAKER_MODEL_TYPE}
                    />
                  </FormField>
                  <FormField label="Sagemaker Endpoint">
                    <Input {...bindSagemakerEndpoint} />
                  </FormField>
                  <FormField label="Embedding Endpoint">
                    <Input {...bindEmbeddingEndpoint} />
                  </FormField>
                </>
              ) : (
                <>
                  <FormField label="Model Type">
                    <Select
                      selectedOption={{ value: thirdPartyModelType }}
                      onChange={({ detail }) =>
                        setThirdPartyApiOption(detail.selectedOption.value)
                      }
                      options={THIRD_PARTY_APIS}
                    />
                  </FormField>
                  <FormField label="Model Name">
                    {/* <Input {...bindModelName} /> */}
                    <Select
                      selectedOption={{ value: thirdPartyModelName }}
                      onChange={({ detail }) =>
                        setThirdPartyModelName(detail.selectedOption.value)
                      }
                      options={THIRD_PARTY_API_MODEL_NAME}
                    />
                  </FormField>
                  <FormField label="Endpoint / API Key">
                    <Input {...bindEndpointOrApiKey} />
                  </FormField>
                </>
              )}
            </SpaceBetween>
          </Form>
        </form>
      </Container>
    </SpaceBetween>
  );
};

export default AddLanguageModel;
