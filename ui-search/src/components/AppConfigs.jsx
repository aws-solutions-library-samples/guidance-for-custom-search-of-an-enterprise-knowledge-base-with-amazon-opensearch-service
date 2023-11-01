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
  Tiles,
} from '@cloudscape-design/components';
import {
  Density,
  Mode,
  applyDensity,
  applyMode,
} from '@cloudscape-design/global-styles';
import toast from 'react-hot-toast';
import useLsAppConfigs, { INIT_APP_CONFIGS } from 'src/hooks/useLsAppConfigs';
import useLsSessionList from 'src/hooks/useLsSessionList';
import genDefaultSessions from 'src/utils/genDefaultSessions';

const SEARCH_METHOD = [
  { label: 'vector', value: 'vector' },
  { label: 'text', value: 'text' },
  { label: 'mix', value: 'mix' },
];

const AppConfigs = () => {
  const { setLsSessionList, lsAddSessionItem } = useLsSessionList();
  const { appConfigs, setAConfig, setAppConfigs } = useLsAppConfigs();

  return (
    <Container header={<Header>Application Configuration</Header>}>
      <form>
        <Form>
          <SpaceBetween size="l">
            <FormField
              stretch
              label="WebSocket URL"
              description="For basic chat bot functions"
            >
              <Input
                value={appConfigs.urlWss}
                onChange={({ detail }) => {
                  setAConfig('urlWss', detail.value);
                }}
              />
            </FormField>
            <FormField
              stretch
              label="API Gateway URL"
              description="For upload files functions"
            >
              <Input
                value={appConfigs.urlApiGateway}
                onChange={({ detail }) => {
                  setAConfig('urlApiGateway', detail.value);
                }}
              />
            </FormField>
            <FormField
              stretch
              label="S3 Bucket Name"
              description="Where files can be uploaded to"
            >
              <Input
                value={appConfigs.s3FileUpload}
                onChange={({ detail }) => {
                  setAConfig('s3FileUpload', detail.value);
                }}
              />
            </FormField>
            <FormField
              stretch
              label="Token for Content Check"
              description="Set to enable the ability to check content"
            >
              <Input
                value={appConfigs.tokenContentCheck}
                onChange={({ detail }) => {
                  setAConfig('tokenContentCheck', detail.value);
                }}
              />
            </FormField>
            <FormField
              stretch
              label="Response if no doc is found"
              description=""
            >
              <Input
                value={appConfigs.responseIfNoDocsFound}
                onChange={({ detail }) => {
                  setAConfig('responseIfNoDocsFound', detail.value);
                }}
              />
            </FormField>
            <SpaceBetween direction="horizontal" size="xxl">
              <FormField stretch label="Search method" description="检索方式">
                <Select
                  selectedOption={{ value: appConfigs.searchMethod }}
                  onChange={({ detail }) =>
                    setAConfig('searchMethod', detail.selectedOption.value)
                  }
                  options={SEARCH_METHOD}
                />
              </FormField>
              <FormField
                stretch
                label="Numbers of doc to search"
                description="文本检索的文档数量 (1-10)"
                errorText={
                  appConfigs.txtDocsNum >= 0 && appConfigs.txtDocsNum <= 10
                    ? ''
                    : 'A number between 0 and 10'
                }
              >
                <Input
                  onBlur={() =>
                    appConfigs.txtDocsNum !== 0 && !appConfigs.txtDocsNum
                      ? setAConfig('txtDocsNum', 0)
                      : null
                  }
                  step={1}
                  type="number"
                  inputMode="decimal"
                  value={appConfigs.txtDocsNum}
                  onChange={({ detail }) => {
                    setAConfig('txtDocsNum', detail.value);
                  }}
                />
              </FormField>
              <FormField
                stretch
                label="Threshold for vector search"
                description="向量检索的分数阈值 (0-1)"
                errorText={
                  appConfigs.vecDocsScoreThresholds >= 0 &&
                  appConfigs.vecDocsScoreThresholds <= 1
                    ? ''
                    : 'A number between 0 and 1'
                }
              >
                <Input
                  onBlur={() =>
                    appConfigs.vecDocsScoreThresholds !== 0 &&
                    !appConfigs.vecDocsScoreThresholds
                      ? setAConfig('vecDocsScoreThresholds', 0)
                      : null
                  }
                  step={0.01}
                  type="number"
                  value={appConfigs.vecDocsScoreThresholds}
                  onChange={({ detail }) => {
                    setAConfig('vecDocsScoreThresholds', detail.value);
                  }}
                />
              </FormField>
              <FormField
                stretch
                label="Threshold for text search"
                description="文本检索的分数阈值 (0-1)"
                errorText={
                  appConfigs.txtDocsScoreThresholds >= 0 &&
                  appConfigs.txtDocsScoreThresholds <= 1
                    ? ''
                    : 'A number between 0 and 1'
                }
              >
                <Input
                  onBlur={() =>
                    appConfigs.txtDocsScoreThresholds !== 0 &&
                    !appConfigs.txtDocsScoreThresholds
                      ? setAConfig('txtDocsScoreThresholds', 0)
                      : null
                  }
                  step={0.01}
                  type="number"
                  value={appConfigs.txtDocsScoreThresholds}
                  onChange={({ detail }) => {
                    setAConfig('txtDocsScoreThresholds', detail.value);
                  }}
                />
              </FormField>
            </SpaceBetween>
            <FormField
              stretch
              label="Visual Modes"
              description="Visual modes are used to optimize the user interface based on environmental conditions and user preferences."
            >
              <Tiles
                value={appConfigs.mode}
                onChange={({ detail }) => {
                  setAConfig('mode', detail.value);
                  applyMode(detail.value === 'light' ? Mode.Light : Mode.Dark);
                }}
                items={[
                  {
                    value: 'light',
                    label: 'Light Mode',
                    description:
                      'This mode is suitable for reading large amounts of text, due to the background and text color combination. It also facilitates consuming several information blocks at once, rather than focusing on a very specific task, making it easy for the eye to scan all the elements in one page.',
                  },
                  {
                    value: 'dark',
                    label: 'Dark Mode',
                    description:
                      'The dark mode provides the user with greater focus, sequences the different content areas on the screen, and improves productivity in highly interactive interfaces. ',
                  },
                ]}
              />
            </FormField>
            <FormField
              stretch
              label="Content Density"
              description="Content density is defined by the ratio of information visible compared to the space available in the interface"
            >
              <Tiles
                value={appConfigs.density}
                onChange={({ detail }) => {
                  setAConfig('density', detail.value);
                  applyDensity(
                    detail.value === 'comfortable'
                      ? Density.Comfortable
                      : Density.Compact
                  );
                }}
                items={[
                  {
                    value: 'comfortable',
                    label: 'Comfortable',
                    description:
                      'Comfortable is the standard density level of the system, active by default. It optimizes content consumption and readability, as well as cross device experiences.',
                  },
                  {
                    value: 'compact',
                    label: 'Compact',
                    description:
                      'Compact is an additional density level for data intensive views. It increases the visibility of large amounts of data by reducing the space between elements on the screen.',
                  },
                ]}
              />
            </FormField>
            <Box float="right" margin="l">
              <SpaceBetween size="s" direction="horizontal">
                <Button
                  iconName="download"
                  onClick={() => {
                    genDefaultSessions().forEach((session) =>
                      lsAddSessionItem(session)
                    );
                    toast('Default sessions imported successfully!');
                  }}
                >
                  Import default sessions
                </Button>
                <Button
                  iconName="remove"
                  onClick={() => {
                    const bool = confirm('Confirm to clear all sessions?');
                    if (bool) {
                      if (process.env.NODE_ENV === 'development') {
                        // TESTING
                        setLsSessionList((prev) =>
                          prev.length > 0
                            ? [
                                {
                                  ...prev[0],
                                  conversations: prev[0].conversations.slice(
                                    0,
                                    10
                                  ),
                                },
                              ]
                            : []
                        );
                      } else {
                        setLsSessionList([]);
                      }
                    }
                  }}
                >
                  Clear sessions
                </Button>
                <Button
                  iconName="remove"
                  onClick={() => {
                    const bool = confirm(
                      'Confirm to reset all configs for the app?'
                    );
                    if (bool) setAppConfigs(INIT_APP_CONFIGS);
                  }}
                >
                  Reset All App Configs
                </Button>
              </SpaceBetween>
            </Box>
          </SpaceBetween>
        </Form>
      </form>
    </Container>
  );
};

export default AppConfigs;
