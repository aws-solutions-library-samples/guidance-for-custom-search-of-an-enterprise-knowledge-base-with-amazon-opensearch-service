// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import React from 'react';
import { CollectionPreferences} from '@cloudscape-design/components';


const VISIBLE_CONTENT_OPTIONS = [
  {
    label: 'Main distribution properties',
    options: [
      { id: '_feedback', label: 'Feedback' },
      { id: '_id', label: 'ID' },
      { id: 'title', label: 'title' },
      { id: 'sentence', label: ' sentence' },
      { id: 'paragraph', label: 'paragraph' },
      { id: 'sentence_id', label: 'sentence_id' },
      { id: 'paragraph_id', label: 'paragraph_id' },
      // { id: 'priceClass', label: 'Price class' },
      // { id: 'sslCertificate', label: 'SSL certificate' },
      // { id: 'origin', label: 'Origin' },
      // { id: 'status', label: 'Status' },
      { id: '_score', label: 'Score' },
      // { id: 'logging', label: 'Logging' },
    ],
  },
];

export const PAGE_SIZE_OPTIONS = [
  { value: 10, label: '10 Distributions' },
  { value: 30, label: '30 Distributions' },
  { value: 50, label: '50 Distributions' },
];

export const DEFAULT_PREFERENCES = {
  pageSize: 50,
  visibleContent: ['_feedback', '_score', 'title', 'sentence', 'paragraph', 'sentence_id', 'paragraph_id'],
  wrapLines: false,
};

export const Preferences = ({
  preferences,
  setPreferences,
  disabled,
  pageSizeOptions = PAGE_SIZE_OPTIONS,
  visibleContentOptions = VISIBLE_CONTENT_OPTIONS,
}) => (
  <CollectionPreferences
    title="Preferences"
    confirmLabel="Confirm"
    cancelLabel="Cancel"
    disabled={disabled}
    preferences={preferences}
    onConfirm={({ detail }) => setPreferences(detail)}
    pageSizePreference={{
      title: 'Page size',
      options: pageSizeOptions,
    }}
    wrapLinesPreference={{
      label: 'Wrap lines',
      description: 'Check to see all the text and wrap the lines',
    }}
    visibleContentPreference={{
      title: 'Select visible columns',
      options: visibleContentOptions,
    }}
  />
);
