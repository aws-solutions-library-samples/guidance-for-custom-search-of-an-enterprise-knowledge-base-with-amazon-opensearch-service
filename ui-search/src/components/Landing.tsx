import {
  Box,
  Cards,
  Container,
  SpaceBetween,
  Link,
  ContentLayout,
  Header,
} from '@cloudscape-design/components';
import { styled } from 'styled-components';
import architecture from '../assets/architecture.jpg';
import AppConfigs from './AppConfigs';

const desc = (
  <Box variant="div">
    <p>
      This Guidance demonstrates how to build an application for search based on
      the information in an enterprise knowledge base through the deployment of
      interface nodes, including large language models (LLMs). You can combine
      services to give answers to questions based on your enterprise knowledge
      base with a search engine that provides word segmentation search, fuzzy
      queries, and artificial intelligence (AI) assisted capabilities. This
      Guidance also includes methods such as manual labeling, unsupervised
      clustering, supervised classification, and an LLM to extract guide words.
      Deploying this Guidance can help you automatically split documents into
      paragraphs with embedded vectors to further establish a structured
      enterprise knowledge base.
    </p>
  </Box>
);

const Landing = ({ withConfigs = true }) => {
  return (
    <ContentLayout
      header={
        <Header
          variant="h1"
          description={desc}
          info={
            <Link
              target="_blank"
              href="https://aws.amazon.com/cn/solutions/guidance/custom-search-of-an-enterprise-knowledge-base-on-aws/?did=sl_card&trk=sl_card"
            >
              Info
            </Link>
          }
          // actions={<Button variant="primary">Button</Button>}
        >
          {process.env.REACT_APP_WEB_HEADER}
        </Header>
      }
    >
      <SpaceBetween size="l">
        <Container
          header={
            <Header
              info={
                <Link
                  target="_blank"
                  href="https://aws.amazon.com/cn/solutions/guidance/custom-search-of-an-enterprise-knowledge-base-on-aws/?did=sl_card&trk=sl_card"
                >
                  info
                </Link>
              }
            >
              Architecture Diagram
            </Header>
          }
        >
          <StyledImg src={architecture} alt="" />
        </Container>
        {withConfigs && <AppConfigs />}
      </SpaceBetween>
    </ContentLayout>
  );
};

export default Landing;

const StyledImg = styled.img`
  height: auto;
  width: 100%;
  border-radius: 10px;
`;
