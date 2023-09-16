import React, { useState } from 'react';
import { useCollection } from '@cloudscape-design/collection-hooks';
import { DEFAULT_PREFERENCES, Preferences } from './common/table-config-doc';
import { Pagination, Table, TextFilter, Button, SpaceBetween,Input,StatusIndicator,Grid, FormField, Checkbox } from '@cloudscape-design/components';
import { CustomAppLayout, TableNoMatchState, TableHeader } from './common/common-components';
import { paginationLabels, distributionSelectionLabels, addColumnSortLabels } from './common/labels';
import { getFilterCounterText } from './common/tableCounterStrings';
import { useColumnWidths } from './common/use-column-widths';
import { useLocalStorage } from './common/localStorage';
import { MyNavigation } from './common/mynavigation';

import axios from 'axios'

import {
    mainapi,
    HEADERS,
} from '../pages/common/constants'

var last_search = ''
var last_ml_model = ''
var last_index = 'smart_search_qa_test'
var last_table_name = 'FeedbackRecordsTest'
var last_knn_statue = false
var last_suggestion_answer = ''

// const api = mainapi + '/search_knn_doc'
const api = mainapi + '/langchain_processor_qa'

function ResponseIcon({ _item }){
  const [upVariant, setUpVariant] = useState("icon" );
  const [downVariant, setDownVariant] = useState("icon");
  const [upStyle, setUpStyle] = useState("caret-up-filled" );
  const [downStyle, setDownStyle] = useState("caret-down-filled");

  function insertFeedback (
    search_inputs,
    _id,
    datetime,
    feedback,
  ) {
    const pyload = {
      "Method": "insert_feedback",
      "table_name": "FeedbackRecordsKingdeeSkuMaterial",
      "datetime": datetime,
      "search_inputs": search_inputs,
      "_id": _id,
      "feedback": feedback
      // "Access-Control-Allow-Origin": 'true'
    }
  console.log(pyload)
  axios({ method: 'POST', url: mainapi, data: pyload, headers: HEADERS}).then(response => {
    console.log(response);
    })
  }

  const upDataIncon = (e,
    up=false,
   ) => {
    if (up){
      setUpVariant("primary")
      setDownVariant("icon")
      // console.log('*********##########x')
      // console.log(_item)
      insertFeedback(last_search, _item._id, _item.datetime, 1)
      console.log(_item)
    }
    else{
      setUpVariant("icon")
      setDownVariant("primary")
      insertFeedback(last_search, _item._id, _item.datetime, 0)
    }
    return up;
  }
  return (
  <div>
    <Button iconName={upStyle} variant={upVariant} onClick={(e)=>upDataIncon(e, true)}/>
    <Button iconName={downStyle} variant={downVariant} onClick={(e)=>upDataIncon(e, false)}/>
  </div>
  );
}

const COLUMN_DEFINITIONS = addColumnSortLabels([
  {
    id: '_id',
    sortingField: '_id',
    // header: 'Distribution ID',
    header: 'ID',
    cell: item => item._id,
    minWidth: 100,
  },
  {
    id: '_feedback',
    sortingField: '_feedback',
    // header: 'Distribution ID',
    header: 'Feedback',
    // cell: item => item._id,
    cell: item => (
      <div>
        <ResponseIcon _item={item}/>
      </div>
    ),
    minWidth: 100,
  },
  {
    id: '_score',
    sortingField: '_score',
    header: 'Score',
    cell: item => (
      <StatusIndicator type={item.state === 'Deactivated' ? 'error' : 'success'}>{item._score}</StatusIndicator>
    ),
    minWidth: 120,
  },
  {
    id: 'title',
    sortingField: 'title',
    cell: item => item.title,
    header: 'title',
    minWidth: 100,
  },
  {
    id: 'sentence',
    sortingField: 'sentence',
    header: 'sentence',
    cell: item => item.sentence,
    minWidth: 100,
  },
  {
    id: 'paragraph',
    sortingField: 'paragraph',
    header: 'paragraph',
    cell: item => item.paragraph,
    minWidth: 100,
  },
  {
    id: 'sentence_id',
    sortingField: 'sentence_id',
    header: 'sentence_id',
    cell: item => item.sentence_id,
    minWidth: 100,
  },
  {
    id: 'paragraph_id',
    sortingField: 'paragraph_id',
    header: 'paragraph_id',
    cell: item => item.paragraph_id,
    minWidth: 100,
  }
]);


function TableContent({ distributions, updateTools }) {
  const [columnDefinitions, saveWidths] = useColumnWidths('React-Table-Widths', COLUMN_DEFINITIONS);
  const [preferences, setPreferences] = useLocalStorage('React-DistributionsTable-Preferences', DEFAULT_PREFERENCES);
  const [new_items, setNewItems] = useState([])
  const [suggestionAnswer, setSuggestionAnswer] = useState(last_suggestion_answer)

  const updateItems = (e,
    query = 5,
    withML = 10,
   ) => {
    setNewItems(getTopData(distributions, query))
  }

  function getTopData(items, top) {
    var i = 0;
    var selected = []
    while (i < top) {
      selected.push(items[i]);
        i++;
    }
    return selected;
  }

  const search = (e,
    query = '',
    ind = '',
    withML = '',
    knn = false,
    with_last_search = false
   ) => {
    setNewItems([])
    if (query == ''){
      last_search=''
    }
    if (with_last_search){
      query = last_search + ' ' + query
    }
    console.log('*************')
    console.log(query)
    if (withML == ''){
      var apiurl = api + '?q=' + query + '&ind=' + ind
    }
    else{
      var apiurl = api + '?q=' + query + '&ind=' + ind + '&ml=' + withML
    }

    if (knn == true){
      apiurl = apiurl + '&knn=1'
    }
    else{
      apiurl = apiurl + '&knn=0'
    }

    if (api.search("langchain_processor_qa") > 0){
      apiurl += '&response_type=web_ui'
    }

    last_search = query
    last_ml_model = withML
    last_index = ind
    last_knn_statue = knn

    console.log(apiurl);
    axios({ method: 'GET', url: apiurl, headers: HEADERS}).then(response => {
      // console.log(response);

      if (response.data.body){
        console.log(response.data)
        var _tmp_data = []
        if (api.search("langchain_processor_qa") > 0){
          response.data.body.forEach((item)=>{
              var _tmp = {}
              _tmp['_id'] = item['_id']
              _tmp['_score'] = item['_score']
              _tmp['title'] = item['title']
              _tmp['sentence'] = item['sentence']
              _tmp['paragraph'] = item['paragraph']
              _tmp['sentence_id'] = item['sentence_id']
              _tmp['paragraph_id'] = item['paragraph_id']
              _tmp['datetime'] = response.data.datetime
              _tmp_data.push(_tmp)
          });
        }else{
          response.data.body.hits.hits.forEach((item)=>{
            var _tmp = {}
            _tmp['_id'] = item['_id']
            _tmp['_score'] = item['_score']
            _tmp['title'] = item['_source']['title']
            _tmp['sentence'] = item['_source']['sentence']
            _tmp['paragraph'] = item['_source']['paragraph']
            _tmp['sentence_id'] = item['_source']['sentence_id']
            _tmp['paragraph_id'] = item['_source']['paragraph_id']
            _tmp['datetime'] = response.data.datetime
            _tmp_data.push(_tmp)
          });
        }  
        
        setSuggestionAnswer(response.data.suggestion_answer)
        setNewItems(_tmp_data)
        // setNewIndex(response.data.generated_index_with_number)
        // setNewIndexOnly(response.data.generated_index_only)
        last_search = query
        last_ml_model = withML
        last_index = ind
        last_knn_statue = knn
    }
    return response;
    })
  }

  const { items, actions, filteredItemsCount, collectionProps, filterProps, paginationProps } = useCollection(
    new_items,
    {
      filtering: {
        // empty: <TableEmptyState resourceName="Distribution" />,
        noMatch: <TableNoMatchState onClearFilter={() => actions.setFiltering()} />,
      },
      pagination: { pageSize: preferences.pageSize },
      sortingDescending: { defaultState: { sortingColumn: columnDefinitions[1] } },
      selection: {},
    }
  );

  const FullPageHeader = ({
    resourceName = 'Filter',
    // createButtonText = 'Filter',
    ...props
  }) => {
    const isOnlyOneSelected = props.selectedItems.length === 1;
  
    return (
      <TableHeader
        // variant="awsui-h1-sticky"
        title={resourceName}
        {...props}
      />
    );
  };

  const SearchWithFilter = ({
    resourceName = 'Search Results',
    createButtonText = 'Search',
    ...props
  }) => {
    const isOnlyOneSelected = props.selectedItems.length === 1;
  
    return (
      <TableHeader
        // variant="awsui-h1-sticky"
        title={resourceName}
        actionButtons={
          <SpaceBetween size="xs" direction="horizontal">
            <Button variant="primary" onClick={updateItems}>{createButtonText}</Button>
          </SpaceBetween>
        }
        {...props}
      />
    );
  };

  const MainSearch = () => {
    const [ filteringText, setFilteringText] = useState(last_search);
    const [ modeName, setModeName] = useState(last_ml_model);
    const [ indexName, setIndexName] = useState(last_index);
    const [ knnEnable, setKnnEnable] = React.useState(last_knn_statue);
    const [ dynamoDBTableName, setDynamoDBTableName] = useState(last_table_name);
    return (
      <SpaceBetween size="xxs" direction="vertical">
        <SpaceBetween size="xxs" direction="vertical">
          <Input
            onChange={({ detail }) => setFilteringText(detail.value)}
            value={filteringText}
            placeholder="输入搜索内容"
          />
          <SpaceBetween size="s" direction="horizontal">
            <FormField
                constraintText="ML Model Name"
              >
              <Input
                onChange={({ detail }) => setModeName(detail.value)}
                value={modeName}
                placeholder="输入ML模型"
              />
            </FormField>

            <FormField
              constraintText="Index Name"
             >
              <Input
                onChange={({ detail }) => setIndexName(detail.value)}
                value={indexName}
                placeholder="index name"
              />
            </FormField>
            <Checkbox
              onChange={({ detail }) =>
                setKnnEnable(detail.checked)
              }
              checked={knnEnable}
              description="Approximate k-NN search"
            >
              Enable
            </Checkbox>
            <Button variant="primary" onClick={(e)=>search(e, filteringText, indexName, modeName, knnEnable)}>{'Search'}</Button>
          </SpaceBetween>
        </SpaceBetween>
        <h3>Suggestion Answer</h3>
        <h4>{suggestionAnswer}</h4>
      </SpaceBetween>
    );
  }
  

  return (
    <Grid
      gridDefinition={[
        { colspan: { l: 12, m: 12, default: 12 } },
        { colspan: { l: 12, m: 12, default: 12 } },
        { colspan: { l: 12, m: 12, default: 12 } },
      ]}
    >
      <Button variant="link" disabled>{''}</Button>
      <MainSearch />
      <Table
        {...collectionProps}
        columnDefinitions={columnDefinitions}
        visibleColumns={preferences.visibleContent}
        items={items}
        selectionType="multi"
        ariaLabels={distributionSelectionLabels}
        // variant="full-page"
        stickyHeader={true}
        resizableColumns={true}
        onColumnWidthsChange={saveWidths}
        wrapLines={preferences.wrapLines}
        header={
          <FullPageHeader
            selectedItems={collectionProps.selectedItems}
            totalItems={new_items}
            // updateTools={updateTools}
          />
        }
        filter={
          <TextFilter
            {...filterProps}
            filteringAriaLabel="Filter distributions"
            filteringPlaceholder="输入过滤词"
            countText={getFilterCounterText(filteredItemsCount)}
            // onChange={updateItems}
          />
        }
        pagination={<Pagination {...paginationProps} ariaLabels={paginationLabels} />}
        preferences={<Preferences preferences={preferences} setPreferences={setPreferences} />}
      />
    </Grid>
  );
}

function App({ distributions }) {
  const [toolsOpen, setToolsOpen] = useState(false);
  const [activeHref, setActiveHref] = React.useState(
    "#/Search"
  );
  return (
    <CustomAppLayout
      // navigation={<Navigation activeHref="#/distributions" />}
      navigation={<MyNavigation />}
      // notifications={<Notifications successNotification={true} />}
      // breadcrumbs={<Breadcrumbs />}
      content={<TableContent distributions={distributions} updateTools={() => setToolsOpen(true)} />}
      contentType="table"
      // tools={<ToolsContent />} 
      // toolsOpen={toolsOpen}
      // onToolsChange={({ detail }) => setToolsOpen(detail.open)}
      stickyNotifications
    />
  );
}



function SearchMain() {
    return (
      <App />
    );
  }
  
  export default SearchMain;